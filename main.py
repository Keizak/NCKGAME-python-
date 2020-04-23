import sys
from time import sleep
import pygame
from settings import Settings
from game_stats import GameStats
from ship import Ship
from bullet import Bullet
from girl import Girl
from button import Button



class NCKGAME:
    """"Класс для управления ресурсами и поведенем игры"""
    def __init__(self):
        pygame.init()
        self.settings = Settings()
        self.screen = pygame.display.set_mode((self.settings.screen_width,self.settings.screen_height))
        pygame.display.set_caption("NCK GAME")
        self.stats = GameStats(self)
        self.ship = Ship(self)
        self.bullets = pygame.sprite.Group()
        self.girls = pygame.sprite.Group()

        self.play_button = Button(self, "Play")
        self._create_fleet()

    def run_game(self):
        """"Запуск основного цикла игры"""

        while True:
            self._check_events()
            if self.stats.game_active:
                self.ship.update()
                self.bullets.update()
                self._update_bullets()
                self._update_girls()
            self._update_events()





    def _check_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                self._check_keydown_events(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                self._check_play_button(mouse_pos)
            elif event.type == pygame.KEYUP:
                self._check_keyup_events(event)


    def _update_events(self):
        self.screen.fill(self.settings.bg_color)
        self.ship.blitme()
        for bullet in self.bullets.sprites():
            bullet.draw_bullets()
        self.girls.draw(self.screen)
        if not self.stats.game_active :
            self.play_button.draw_button()
        pygame.display.flip()


    def _check_keydown_events(self,event):
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = True
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = True
        elif event.key == pygame.K_q:
            sys.exit()
        elif event.key == pygame.K_SPACE :
            self._fire_bullet()

    def _check_keyup_events(self,event):
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = False
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = False

    def _fire_bullet(self):
        if len(self.bullets) < self.settings.bullet_allowed:
            new_bullet = Bullet(self)
            self.bullets.add(new_bullet)

    def _update_bullets(self):
        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)
        self._check_collusion()

    def _check_collusion(self):
        collusions = pygame.sprite.groupcollide(self.bullets, self.girls, True, True)
        if not self.girls:
            self.bullets.empty()
            self._create_fleet()


    def _create_fleet(self):
        girl = Girl(self)
        girl_width, girl_height = girl.rect.size
        availible_space_x = self.settings.screen_width - (2 * girl_width)
        numbers_girls_x = availible_space_x // ( 2 * girl_width)
        ship_height = self.ship.rect.height
        availible_space_y = self.settings.screen_height - (3 * girl_height) - ship_height
        numbers_rows = availible_space_y // (2 * girl_height)
        for row_number in range(numbers_rows):
            for girl_number in range(numbers_girls_x):
                self._create_girl(girl_number,row_number)

    def _create_girl (self,girl_number,row_number):
        girl = Girl(self)
        girl_width, girl_height = girl.rect.size
        girl.x = girl_width + 2 * girl_width * girl_number
        girl.rect.x = girl.x
        girl.rect.y = girl.rect.height + 2 * girl.rect.height * row_number
        self.girls.add(girl)

    def _update_girls(self):
        self._check_fleet_edges()
        self.girls.update()
        if pygame.sprite.spritecollideany(self.ship, self.girls) :
            self._ship_hit()
        self._check_aliens_bottom()

    def _check_fleet_edges(self):
        for girl in self.girls.sprites():
            if girl.check_edges():
                self._change_fleet_direction()
                break


    def _change_fleet_direction(self):
        for girl in self.girls.sprites():
            girl.rect.y += self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1

    def _ship_hit(self):
        if self.stats.ships_left > 0:
            self.stats.ships_left -= 1
            self.girls.empty()
            self.bullets.empty()
            self._create_fleet()
            self.ship.center_ship()
            sleep(0.5)
        else:
            self.stats.game_active = False

    def _check_aliens_bottom(self):
        screen_rect =  self.screen.get_rect()
        for girl in self.girls.sprites():
            if girl.rect.bottom >= screen_rect.bottom:
                self._ship_hit()
                break

    def _check_play_button(self,mouse_pos):
        button_clicked = self.play_button.rect.collidepoint(mouse_pos)
        if button_clicked and not self.stats.game_active :
            self.stats.reset_stats()
            self.stats.game_active = True

            self.girls.empty()
            self.bullets.empty()

            self._create_fleet()
            self.ship.center_ship()


if __name__ == '__main__':
    ai = NCKGAME()
    ai.run_game()