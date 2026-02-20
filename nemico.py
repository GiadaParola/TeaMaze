import pygame
import random


class Nemico:
    """Nemico che segue path di tile percorribili e si muove centrato sui tile.

    Il nemico riceve `grid_info` da `main.py`, che contiene:
      - 'passable': set di tuple (tx,ty) percorribili
      - 'tile_w', 'tile_h', 'map_w', 'map_h'

    Comportamento:
      - Sceglie una destinazione casuale tra i tile percorribili e calcola
        un percorso con BFS (4-vicini).
      - Si muove fluentemente centro->centro dei tile lungo il percorso.
      - Quando arriva a destinazione sceglie una nuova meta.
    """

    def __init__(self, x, y, img, grid_info, speed=1):
        self.image = pygame.transform.scale(img, (35, 35))
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = speed
        self.grid = grid_info
        self.passable = grid_info.get('passable', set())
        self.tw = grid_info.get('tile_w', 32)
        self.th = grid_info.get('tile_h', 32)
        self.map_w = grid_info.get('map_w', 0)
        self.map_h = grid_info.get('map_h', 0)

        # current tile coordinate
        cx, cy = self.rect.center
        self.tile = (cx // self.tw, cy // self.th)

        # path: list of tile coords to visit (excluding current tile)
        self.path = []
        self.target = None

    def _tile_center(self, t):
        tx, ty = t
        return (tx * self.tw + self.tw // 2, ty * self.th + self.th // 2)

    def _neighbors(self, t):
        x, y = t
        for nx, ny in ((x+1,y),(x-1,y),(x,y+1),(x,y-1)):
            if 0 <= nx < self.map_w and 0 <= ny < self.map_h and (nx, ny) in self.passable:
                yield (nx, ny)

    def _bfs(self, start, goal):
        from collections import deque
        q = deque([start])
        prev = {start: None}
        while q:
            cur = q.popleft()
            if cur == goal:
                break
            for nb in self._neighbors(cur):
                if nb not in prev:
                    prev[nb] = cur
                    q.append(nb)
        if goal not in prev:
            return []
        # ricostruisci percorso
        path = []
        cur = goal
        while cur != start:
            path.append(cur)
            cur = prev[cur]
        path.reverse()
        return path

    def _choose_new_target(self):
        if not self.passable:
            return None
        # escludi tile corrente
        choices = list(self.passable - {self.tile})
        if not choices:
            return None
        return random.choice(choices)

    def muovi_auto(self, muri, *_args, **_kwargs):
        """Aggiorna la posizione del nemico seguendo il percorso di tile.

        Firma compatibile con chiamate esistenti che passano `muri` e opzionali
        altri argomenti.
        """
        # se non ho percorso, scegli una destinazione e calcola percorso
        if not self.path:
            self.tile = (self.rect.centerx // self.tw, self.rect.centery // self.th)
            dest = self._choose_new_target()
            if dest:
                self.path = self._bfs(self.tile, dest)
                if self.path:
                    self.target = self.path.pop(0)
                else:
                    self.target = None

        # se ho un target tile, muoviti verso il suo centro
        if self.target:
            tx, ty = self._tile_center(self.target)
            cx, cy = self.rect.center
            vx = tx - cx
            vy = ty - cy
            # movimento solo su assi (i tile sono adiacenti)
            if vx != 0:
                step = self.speed if abs(vx) > self.speed else abs(vx)
                self.rect.centerx += step if vx > 0 else -step
            elif vy != 0:
                step = self.speed if abs(vy) > self.speed else abs(vy)
                self.rect.centery += step if vy > 0 else -step

            # raggiunto il centro del tile target?
            if abs(tx - self.rect.centerx) <= 0 and abs(ty - self.rect.centery) <= 0 or (abs(tx - self.rect.centerx) <= self.speed and abs(ty - self.rect.centery) <= self.speed):
                # snap esatto
                self.rect.center = (tx, ty)
                # aggiorna tile
                self.tile = self.target
                # prendi prossimo
                if self.path:
                    self.target = self.path.pop(0)
                else:
                    self.target = None

    def draw(self, surface, camera_pos):
        surface.blit(self.image, (self.rect.x - camera_pos[0], self.rect.y - camera_pos[1]))