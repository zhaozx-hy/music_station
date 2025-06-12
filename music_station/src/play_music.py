import pygame
import os
import time

# 初始化Pygame
pygame.init()
pygame.mixer.init()

# 创建窗口
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("简易音乐播放器")

# 颜色定义
BACKGROUND = (30, 30, 40)
SIDEBAR = (50, 50, 65)
LIST_HIGHLIGHT = (70, 130, 180)
BUTTON_NORMAL = (100, 150, 200)
BUTTON_HOVER = (120, 180, 220)
TEXT_COLOR = (220, 220, 220)
TEXT_HIGHLIGHT = (255, 255, 255)

# 字体
font_small = pygame.font.SysFont(None, 24)
font_medium = pygame.font.SysFont(None, 32)
font_large = pygame.font.SysFont(None, 48)


# 获取music文件夹中的所有歌曲
def get_music_files():
    music_dir = '../music'
    music_files = []

    if os.path.exists(music_dir):
        for file in os.listdir(music_dir):
            if file.lower().endswith(('.mp3', '.wav', '.ogg')):
                music_files.append(os.path.join(music_dir, file))

    return music_files


# 播放器状态
class PlayerState:
    def __init__(self):
        self.music_files = get_music_files()
        self.current_index = 0
        self.playing = False
        self.paused = False
        self.current_song = ""

        if self.music_files:
            self.current_song = self.music_files[0]

    def play(self, index=None):
        if index is not None and 0 <= index < len(self.music_files):
            self.current_index = index
            self.current_song = self.music_files[index]

        try:
            pygame.mixer.music.load(self.current_song)
            pygame.mixer.music.play()
            self.playing = True
            self.paused = False
        except Exception as e:
            print(f"播放错误: {e}")

    def pause(self):
        if self.playing and not self.paused:
            pygame.mixer.music.pause()
            self.paused = True

    def unpause(self):
        if self.playing and self.paused:
            pygame.mixer.music.unpause()
            self.paused = False

    def stop(self):
        pygame.mixer.music.stop()
        self.playing = False
        self.paused = False

    def next(self):
        if len(self.music_files) > 0:
            new_index = (self.current_index + 1) % len(self.music_files)
            self.play(new_index)

    def prev(self):
        if len(self.music_files) > 0:
            new_index = (self.current_index - 1) % len(self.music_files)
            self.play(new_index)


# 创建播放器状态
player = PlayerState()


# 按钮类
class Button:
    def __init__(self, x, y, width, height, text, action=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.hover = False

    def draw(self, surface):
        color = BUTTON_HOVER if self.hover else BUTTON_NORMAL
        pygame.draw.rect(surface, color, self.rect, border_radius=5)
        pygame.draw.rect(surface, TEXT_COLOR, self.rect, 2, border_radius=5)

        text_surf = font_medium.render(self.text, True, TEXT_COLOR)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def check_hover(self, pos):
        self.hover = self.rect.collidepoint(pos)
        return self.hover

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.hover and self.action:
                self.action()
                return True
        return False


# 创建按钮
buttons = [
    Button(WIDTH // 2 - 150, 450, 80, 40, "上一首", player.prev),
    Button(WIDTH // 2 - 50, 450, 100, 40, "播放/暂停",
           lambda: player.unpause() if player.paused else player.pause() if player.playing else player.play()),
    Button(WIDTH // 2 + 60, 450, 80, 40, "下一首", player.next),
    Button(WIDTH // 2 - 40, 500, 120, 40, "停止", player.stop)
]

# 主循环
running = True
clock = pygame.time.Clock()

# 初始播放一首歌
if player.music_files:
    player.play()

while running:
    mouse_pos = pygame.mouse.get_pos()

    # 事件处理
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # 处理按钮点击
        for button in buttons:
            button.handle_event(event)

        # 处理歌曲列表点击
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i, song in enumerate(player.music_files):
                song_rect = pygame.Rect(20, 50 + i * 35, 260, 30)
                if song_rect.collidepoint(mouse_pos):
                    player.play(i)

    # 更新按钮悬停状态
    for button in buttons:
        button.check_hover(mouse_pos)

    # 绘制界面
    screen.fill(BACKGROUND)

    # 绘制侧边栏
    pygame.draw.rect(screen, SIDEBAR, (0, 0, 300, HEIGHT))
    pygame.draw.line(screen, TEXT_COLOR, (300, 0), (300, HEIGHT), 2)

    # 绘制标题
    title = font_large.render("音乐播放器", True, TEXT_HIGHLIGHT)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 20))

    # 绘制歌曲列表
    list_title = font_medium.render("歌曲列表", True, TEXT_HIGHLIGHT)
    screen.blit(list_title, (20, 15))

    for i, song in enumerate(player.music_files):
        # 高亮显示当前播放的歌曲
        color = TEXT_HIGHLIGHT if i == player.current_index else TEXT_COLOR
        song_rect = pygame.Rect(20, 50 + i * 35, 260, 30)

        # 绘制悬停效果
        if song_rect.collidepoint(mouse_pos):
            pygame.draw.rect(screen, LIST_HIGHLIGHT, song_rect, border_radius=3)

        # 绘制当前播放歌曲的高亮
        elif i == player.current_index:
            pygame.draw.rect(screen, (LIST_HIGHLIGHT[0] // 2, LIST_HIGHLIGHT[1] // 2, LIST_HIGHLIGHT[2] // 2),
                             song_rect, border_radius=3)

        # 裁剪歌曲名称以适应宽度
        song_name = os.path.basename(song)
        if len(song_name) > 30:
            song_name = song_name[:27] + "..."

        song_text = font_small.render(f"{i + 1}. {song_name}", True, color)
        screen.blit(song_text, (30, 55 + i * 35))

    # 绘制当前歌曲信息
    if player.current_song:
        song_name = os.path.basename(player.current_song)
        current_text = font_medium.render(f"当前播放: {song_name}", True, TEXT_HIGHLIGHT)
        screen.blit(current_text, (320, 100))

        # 显示播放状态
        status = "播放中" if player.playing and not player.paused else "已暂停" if player.paused else "已停止"
        status_text = font_medium.render(f"状态: {status}", True, TEXT_HIGHLIGHT)
        screen.blit(status_text, (320, 150))

    # 绘制按钮
    for button in buttons:
        button.draw(screen)

    pygame.display.flip()
    clock.tick(60)

# 退出时停止播放
pygame.mixer.music.stop()
pygame.quit()