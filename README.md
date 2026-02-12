# PROJECT AND TEAM PRESENTATION
The project we have developed aims to facilitate the rehabilitation of patients with Amyotrophic Lateral Sclerosis (ALS) through an exergame, a video game based on physical movement. The idea is based on several important aspects:
1. `Motivation and fun` Traditional rehabilitation often involves repetitive and strenuous exercises, which can be boring or demotivating for the patient. By integrating movement into a playful context, the patient experiences the pleasure of play, increasing their motivation to participate in training sessions and prolonging their duration and frequency.
2. `Reduction in the perception of fatigue` The physical exercises necessary to maintain strength, mobility, and coordination can be tiring, especially for patients with ALS, who experience progressive muscle weakness. Exergames partially mask fatigue, as the patient's focus is not only on performing the exercise, but also on the goal of the game and having fun.
3. `Cognitive and sensory involvement` I videogiochi possono stimolare non solo il movimento, ma anche la coordinazione occhio-mano, la percezione spaziale, e la funzione cognitiva. Questo approccio integrato favorisce un allenamento più completo, che va oltre la semplice attività muscolare.
4. `Reducing the psychological burden of illness` Playful experiences can have a positive effect on patients' emotional and psychological well-being. They transform rehabilitation from a mandatory medical task into an enjoyable experience, helping to reduce the emotional fatigue and anxiety associated with illness.
5. `Customization and monitoring` Through the developed system, it is possible to adapt the exercises and level of difficulty based on the patient's abilities, ensuring safe and personalized training, with the ability to monitor progress over time.<br>
<br>
The video game consists of finding your way out of a maze. By answering questions, you can unlock shortcuts that help you reach the end more easily. Players can choose between two characters, a boy and a girl, to play with. They can also choose between three levels with different degrees of difficulty. Along the way, they may encounter monsters that ask a question, which can be answered by choosing from four possible answers. If the answer is correct, a shortcut opens up. To move the characters, we used Muse2, equipped with a gyroscope. We then used head movement to make the character move forward, backward, right, and left.

# ISTRUCTION FOR USE
* It is advisable to use Windows or MacOS as it is not guaranteed the presence of all third-party software on Linux
* In order to use the Muse2, you have to:
  * click on this link and download all the folder: https://github.com/kowalej/BlueMuse , then must unzip this folder: https://github.com/kowalej/BlueMuse/blob/master/DistArchived/BlueMuse_2.0.0.0.zip, and follow his tutorial
  * Then you have to switch on the bluetooth on your pc and start the software of BlueMuse and click on "Start Streaming" and the Muse2 will start to record data.

 # LIBRARIES TO DOWNLOAD
 Not all the libraries used from our project are directly involved in python, these are: pysls, numpy, tkinter, random, scipy, djitellopy, opencv-python, matplotlib and sklearn. So you have to download them writing in the terminal:
* `pip install pysls`, in order to install pysls, a library for DJI drone control.
* `pip install numpy`, in order to install numpy a fundamental library for array manipulation and scientific computing in Python.
* `pip install scipy`, in order to install scipy a library for data processing and analysis in scientific computing.
* `pip install pyqtgraph`, in order to install pyqtgraph a library that allows you to create interactive, high-performance graphs, ideal for displaying scientific or sensory data in real time within applications with Qt interfaces.
* `pip install pylsl`, in order to install pylsl a library for transmitting and receiving data in real time using the Lab Streaming Layer protocol, mainly used to acquire biological signals such as EEG.
* `pip install pygame`, in order to install pygame a library used to create games and multimedia applications by managing graphics, sounds, and user input.

# EXECUTION
You must connect the Muse2 via Bluetooth using his own program.<br>
<br>
After you have to run `TEST/main.py` in the terminal, and wait that the process starts.
