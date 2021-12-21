import time

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ReferenceListProperty
from kivy.vector import Vector
from kivy.clock import Clock

from kivy.core.window import Window

import configparser
import random

# get the config file for the app
config = configparser.ConfigParser()
config.read('config.ini')


# logic for the player paddles
class PongPaddle(Widget):
    score = NumericProperty(0)

    def return_ball(self, ball):
        # if the ball collides with the paddle
        if self.collide_widget(ball):
            # return the ball, make the ball a little faster
            ball.velocity_x *= -1.2


# logic for the ball
class PongBall(Widget):
    velocity_x = NumericProperty(0)
    velocity_y = NumericProperty(0)
    velocity = ReferenceListProperty(velocity_x, velocity_y)

    def move(self):
        # get the current position of the ball and add velocity to it to change the position
        self.pos = Vector(*self.velocity) + self.pos


# overall logi for the game
class PongGame(Widget):
    def __init__(self, **kwargs):
        super(PongGame, self).__init__(**kwargs)
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)

    # when the ball is stationary, and needs to start moving
    def serve_ball(self, set_delay=False):
        if set_delay:
            time.sleep(1.8)
        # reset the position of the ball
        self.ball.pos = (self.width / 2, self.height / 2)
        # send the ball in a random direction
        INITIAL_BALL_SPEED = float(config['gameplay']['initialBallSpeed'])
        self.ball.velocity = Vector(INITIAL_BALL_SPEED, 0).rotate(random.randint(0, 360))

    # update the position of the ball
    def update(self, dt):
        # call the function to update the position of the ball
        self.ball.move()
        # check if the either paddles are touching the ball
        self.l_player.return_ball(self.ball)
        self.r_player.return_ball(self.ball)

        # if the ball is going out of the screen vertically, reverse the velocity
        if self.ball.y < 0 or (self.ball.y + self.ball.height) > self.height:
            self.ball.velocity_y *= -1

        # if the ball is going out of the screen behind the left player
        if self.ball.x < 0:
            # add to the score of the right player
            self.r_player.score += 1
            self.serve_ball(True)

        #  if the ball is going out of the screen behind the right player
        if (self.ball.x + self.ball.width) > self.width:
            # add to the score of the left player
            self.l_player.score += 1
            self.serve_ball(True)

    # handle keyboard
    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_press=self._on_keyboard_down)
        self._keyboard = None

    # keyboard events
    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        if keycode[1] == config['controls']['leftPlayerUp']:
            self.l_player.center_y += 10
        elif keycode[1] == config['controls']['leftPlayerDown']:
            self.l_player.center_y -= 10
        elif keycode[1] == config['controls']['rightPlayerUp']:
            self.r_player.center_y += 10
        elif keycode[1] == config['controls']['rightPlayerDown']:
            self.r_player.center_y -= 10
        return True

    # clicks and drag with mouse or touch
    def on_touch_move(self, touch):
        # move the left player if the drag is in the first quarter of the screen
        if touch.x < self.width / 4:
            self.l_player.center_y = touch.y

        # move the right player if the drag is in the last quarter of the screen
        if touch.x > self.width * (3/4):
            self.r_player.center_y = touch.y


class PongApp(App):
    def build(self):
        # set the window to the correct size
        WINDOW_WIDTH = int(config['setup']['width'])
        WINDOW_HEIGHT = int(config['setup']['height'])
        Window.size = (WINDOW_WIDTH, WINDOW_HEIGHT)

        # set game to a set fps
        FPS = float(config['gameplay']['fps'])
        pongGame = PongGame()
        Clock.schedule_interval(pongGame.update, 1.0 / FPS)

        # start the game
        pongGame.serve_ball()

        # draw game to the screen
        return pongGame


if __name__ == '__main__':
    PongApp().run()
