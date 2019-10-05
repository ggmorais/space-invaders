from kivy.config import Config
Config.set('graphics', 'resizable', False)
Config.set('graphics', 'fullscreen', False)

from kivy.app import App
from kivy.graphics import Rectangle, Color, InstructionGroup, BindTexture
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.animation import Animation
from kivy.uix.screenmanager import ScreenManager, Screen

import random


class Game(Widget):
    def __init__(self, **kwargs):
        super(Game, self).__init__(**kwargs)

        self.win_w = Window.size[0]
        self.win_h = Window.size[1]

        ''' Sizes '''
        self.player_size = (self.win_w * .06, self.win_h * .08)
        self.fire_size = (self.player_size[0] / 10, self.player_size[1] / 2)
        self.enemy_size = (self.win_w * .06, self.win_h * .05)
        self.life_size = (self.win_w * .035, self.win_h * .035)

        self.player_init = (self.win_w / 2 - 25, self.win_h / 6)

        self.pressed = set()
        self.firing = False
        self.fires = []
        self.enemies = []
        self.lifes = []
        self.deads = []
        self.move_speed = (self.win_w * self.win_h) * .001
        self.kill_count = 1
        self.dead = False

        self.groups = {
            'foes': InstructionGroup(),
            'bullets': InstructionGroup(),
            'lifes': InstructionGroup(),
            'explosions': InstructionGroup()
        }

        self.groups['bullets'].add(Color(0, .7, 1))

        self.canvas.add(self.groups['foes'])
        self.canvas.add(self.groups['lifes'])
        self.canvas.add(self.groups['explosions'])
        self.canvas.after.add(self.groups['bullets'])

        fire_tex = Image(source='assets/firing.png').texture.get_region(0, 0, 32, 32)

        self.spawn_player()

        self.kill_lbl = Label(text='Score: 0', pos=(self.life_size[0], self.win_h - self.life_size[1] * 4), font_size=30)
        self.add_widget(self.kill_lbl)

        self.restore()

        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._keyboard_down)
        self._keyboard.bind(on_key_up=self._keyboard_up)

        Clock.schedule_interval(self.start, 0)

    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._keyboard_down)
        self._keyboard.unbind(on_key_up=self._keyboard_up)
        self._keyboard = None

    def _keyboard_down(self, keyboard, keycode, text, mod):
        self.pressed.add(keycode[1])

    def _keyboard_up(self, keyboard, keycode):
        if keycode[1] in self.pressed:
            self.pressed.remove(keycode[1])

    def remove_obj(self, obj):
        self.canvas.remove(obj)

    def spawn_player(self, pos=None):
        with self.canvas:
            self.player = Rectangle(size=self.player_size, pos=self.player_init, source='assets/spaceship.png')

    def spawn_enemy(self):
        posx = random.randint(int(self.enemy_size[0]), int(self.win_w - self.enemy_size[0]))
        self.groups['foes'].add(Rectangle(pos=(posx, self.win_h), size=self.enemy_size, source='assets/enemy.png', group='enemy'))

    def stop_firing(self, ms):
        self.firing = False

    def fire(self):
        self.firing = True
        self.groups['bullets'].add(Rectangle(pos=(self.player.pos[0] + self.player_size[0] / 2.2, self.player.pos[1] + self.player.size[1]), size=self.fire_size))
        Clock.schedule_once(self.stop_firing, .1)

    def explode(self, obj):
        tex = Image(source='asssts/explosion_animate.png').texture
        tex = tex.get_region(0, 0, 32, 32)
        x = Rectangle(size=obj.size, pos=obj.pos, texture=tex)

    def restore(self, btn=None):
        self.life_count = 3
        self.kill_count = 0
        for x in range(self.life_count):
            if len(self.get_children('lifes')) < self.life_count:
                if len(self.get_children('lifes')) == 0:
                    self.groups['lifes'].add(Rectangle(size=self.life_size, pos=self.life_size, source='assets/life.png'))
                else:
                    self.groups['lifes'].add(Rectangle(size=self.life_size, pos=(self.get_children('lifes')[-1].pos[0] + self.get_children('lifes')[-1].size[0], self.life_size[1]), source='assets/life.png'))

    def remove_explosion(self, ms):
        for dead in self.deads:
            dead.size = (0, 0)

    def show_over(self, ms):
        #self.canvas.remove(self.explosion)
        #self.explosion = False
        self.remove_obj(self.explosion)
        self.life_count = 3
        manager.current = 'GameOver'

    def clear(self):
        self.player.pos = self.player_init
        for enemy in self.enemies:
            self.canvas.remove(enemy)
        for fire in self.fires:
            self.canvas.remove(fire)

    def get_children(self, group):
        children = []
        for child in self.groups[group].children:
            if isinstance(child, BindTexture) is False and isinstance(child, Color) is False:
                children.append(child)

        return children

    def start(self, ms):
        posx = 0
        posy = 0

        player_x = self.player.pos[0]
        player_y = self.player.pos[1]
        player_w = self.player.size[0]
        player_h = self.player.size[1]

        speed = ms * self.move_speed

        firing = False

        if manager.current == 'Game' and len(self.get_children('lifes')) > 0:

            if 'right' in self.pressed:
                posx = speed
            if 'left' in self.pressed:
                posx -= speed

            if player_x + player_w + posx > self.win_w or player_x + posx < 0:
                posx = 0

            if 'spacebar' in self.pressed:
                if self.firing is False:
                    self.fire()

            if len(self.get_children('foes')) < 6:
                self.spawn_enemy()

            for foe in self.get_children('foes'):
                foe.pos = (foe.pos[0], foe.pos[1] - 1)
                if foe.pos[1] < self.player.pos[1]:
                    self.groups['foes'].remove(foe)
                    self.groups['lifes'].remove(self.get_children('lifes')[-1])

            for fire in self.get_children('bullets'):
                fire.pos = (fire.pos[0], fire.pos[1] + speed)
                for enemy in self.get_children('foes'):
                    if fire.pos[1] + fire.size[1] > enemy.pos[1] and fire.pos[0] < enemy.pos[0] + enemy.size[0] and fire.pos[0] + fire.size[0] > enemy.pos[0]:
                        self.kill_count = self.kill_count + 1
                        self.kill_lbl.text = 'Score: ' + str(self.kill_count)

                        with self.canvas.before:
                            self.deads.append(Rectangle(size=(enemy.size[0] - 5, enemy.size[1] - 5), pos=enemy.pos, source='assets/explosion.png'))

                        if len(self.deads) > 0:
                            Clock.schedule_once(self.remove_explosion, .4)

                        self.groups['foes'].remove(enemy)
                        self.groups['bullets'].remove(fire)

                if fire.pos[1] > self.win_h:
                    self.groups['bullets'].remove(fire)

            self.player.pos = (player_x + posx, player_y)
        else:
            #self.canvas.clear()
            self.groups['foes'].clear()
            self.groups['bullets'].clear()
            manager.last_score = 'Your score: ' + str(self.kill_count)
            self.kill_count = 0
            self.kill_lbl.text = 'Score: 0'

            if len(self.get_children('lifes')) == 0:
                manager.current = 'GameOver'


class Start(Widget):
    pass

class GameOver(Widget):
    pass

    def retry(self, btn=None):
        game.restore()
        manager.current = 'Game'

game = Game()

manager = ScreenManager()

class MainApp(App):
    def build(self):
        self.window_size = Window.size



        self.manager = manager

        self.manager.last_score = 'Your score: 0'

        widgets = [
            Start(),
            game,
            GameOver()
        ]

        for wid in widgets:
            sc = Screen(name=wid.__class__.__name__)
            sc.add_widget(wid)
            self.manager.add_widget(sc)

        return self.manager


if __name__ == '__main__':
    MainApp().run()
