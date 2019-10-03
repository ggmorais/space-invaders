from kivy.app import App
from kivy.graphics import Rectangle
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.uix.image import Image
from kivy.graphics import Color
from kivy.uix.button import Button
from kivy.animation import Animation

import random


class Game(Widget):
    def __init__(self, **kwargs):
        super(Game, self).__init__(**kwargs)
        self.win_w = Window.size[0]
        self.win_h = Window.size[1]
        self.pressed = set()
        self.firing = False
        self.fires = []
        self.enemies = []
        self.lifes = []
        self.deads = []
        fire_tex = Image(source='assets/firing.png').texture.get_region(0, 0, 32, 32)
        
        with self.canvas:
            self.player = Rectangle(size=(50, 50), pos=(self.win_w / 2 - 25, self.win_h / 6), source='assets/spaceship.png')
        
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
    
    def spawn_enemy(self):
        posx = random.randint(0, self.win_w) 
        with self.canvas.before:
            self.enemies.append(Rectangle(pos=(posx, self.win_h), size=(40, 30), source='assets/enemy.png'))
    
    def stop_firing(self, ms):
        self.firing = False
    
    def fire(self):
        self.firing = True
        with self.canvas.after:
            Color(0, .7, 1)
            self.fires.append(Rectangle(pos=(self.player.pos[0] + 22, self.player.pos[1] + 55), size=(5, 25)))
            
        Clock.schedule_once(self.stop_firing, .1)
    
    def restore(self, btn=None):
        self.life_count = 3
        with self.canvas:
            for x in range(self.life_count):
                if len(self.lifes) < self.life_count:
                    if len(self.lifes) == 0:
                        self.lifes.append(Rectangle(size=(30, 30), pos=(50, 50), source='assets/life.png'))
                    else:
                        self.lifes.append(Rectangle(size=(30, 30), pos=(self.lifes[-1].pos[0] + self.lifes[-1].size[0] + 10, 50), source='assets/life.png'))
    
    def remove_explosion(self, ms):
        for dead in self.deads:
            dead.size = (0, 0)
    
    def start(self, ms):
        posx = 0
        posy = 0
        
        player_x = self.player.pos[0]
        player_y = self.player.pos[1]
        player_w = self.player.size[0]
        player_h = self.player.size[1]
        
        speed = 500 * ms
        firing = False
        
        if self.life_count == 0:
            with self.canvas.after:
                Rectangle(size=Window.size, source='assets/game_over.png')
            self.add_widget(Button(text='Tentar novamente', on_press=self.restore, size=(200, 50), pos=(self.win_w / 2 - 100, self.win_h / 4)))
        else:
                        
            if 'right' in self.pressed:
                posx = speed
            if 'left' in self.pressed:
                posx -= speed
            
            if player_x + player_w + posx > self.win_w or player_x + posx < 0:
                posx = 0
            
            if 'spacebar' in self.pressed:
                if self.firing is False:
                    self.fire()
            
            if len(self.enemies) < 6:
                self.spawn_enemy()
            
            for enemy in self.enemies:
                enemy.pos = (enemy.pos[0], enemy.pos[1] - 1)
                if enemy.pos[1] < self.player.pos[1] + self.player.size[1]:
                    enemy.pos = (0, 0)
                    enemy.size = (0, 0)
                    self.enemies.remove(enemy)
                    self.life_count -= 1
                    self.lifes[self.life_count].size = (0, 0)
                
            for fire in self.fires:
                fire.pos = (fire.pos[0], fire.pos[1] + speed)
                for enemy in self.enemies:
                    if fire.pos[1] + fire.size[1] > enemy.pos[1] and fire.pos[0] < enemy.pos[0] + enemy.size[0] and fire.pos[0] + fire.size[0] > enemy.pos[0]:
                        
                        with self.canvas.before:
                            self.deads.append(Rectangle(size=(enemy.size[0] - 5, enemy.size[1] - 5), pos=enemy.pos, source='assets/explosion.png'))
                        
                        if len(self.deads) > 0:
                            Clock.schedule_once(self.remove_explosion, .4)
                        
                        self.enemies.remove(enemy)
                        self.fires.remove(fire)
                        fire.size = (0, 0)
                        enemy.size = (0, 0)
                if fire.pos[1] > self.win_h:
                    self.fires.remove(fire)
            
            self.player.pos = (player_x + posx, player_y)
    
    
    
class MainApp(App):
    def build(self):
        return Game()

MainApp().run()
