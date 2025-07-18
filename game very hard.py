import pgzrun
import random

GRID_WIDTH = 17
GRID_HEIGHT = 12
GRID_SIZE = 50
GUARD_MOVE_INTERVAL = 0.25
PLAYER_MOVE_INTERVAL = 0.1
BACKGROUND_SEED = random

WIDTH = GRID_WIDTH * GRID_SIZE
HEIGHT = GRID_HEIGHT * GRID_SIZE
MAP = ["WWWWWWWWWWWWWWWWW",
       "W               W",
       "W               W",
       "W  W   KG       W",
       "W  WWWWWWWWWW   W",
       "W               W",
       "W       P       W",
       "W  WWWWWWWWWW   W",
       "W       GK      W",
       "W               W",
       "W               D",
       "WWWWWWWWWWWWWWWWW"]

def screen_coords(x, y):
    return (x * GRID_SIZE, y * GRID_SIZE)
def grid_coords(actor):
    return (round(actor.x / GRID_SIZE), round(actor.y / GRID_SIZE)) 
def setup_game():
    global game_over, player_won, player, keys_to_collect, guards
    game_over = False
    player_won = False
    player = Actor("player", anchor=("left", "top"))
    keys_to_collect = []
    guards = []
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            square = MAP[y][x]
            if square == "P":
                player.pos = screen_coords(x, y)
            elif square == "K":
                key = Actor("key", anchor=("left", "top"), \
                            pos=screen_coords(x, y))
                keys_to_collect.append(key)
            elif square == "G":
                guard = Actor("guard", anchor=("left", "top"), \
                              pos=screen_coords(x, y))
                guards.append(guard)
def draw_background():
    random.seed(BACKGROUND_SEED)
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            if x % 2 == y % 2:
                screen.blit("floor1", screen_coords(x, y))
            else:
                screen.blit("floor2", screen_coords(x, y))
            n = random.randint(0, 99)
            if n < 5:
                screen.blit("crack1", screen_coords(x, y))
            elif n < 10:
                screen.blit("crack2", screen_coords(x, y))
def draw_scenery():
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            square = MAP[y][x]
            if square == "W":
                screen.blit("wall", screen_coords(x,y))
            elif square == "D" and len(keys_to_collect) > 0:
                screen.blit("door", screen_coords(x,y))
def draw_actors():
    player.draw()
    for key in keys_to_collect:
        key.draw()
    for guard in guards:
        guard.draw()
def draw_game_over():
    screen_middle = (WIDTH / 2, HEIGHT / 2)
    screen.draw.text("GAME OVER", midbottom=screen_middle, \
                     fontsize=GRID_SIZE, color="cyan", owidth=1)
    if player_won:
        screen.draw.text("You won!", midtop=screen_middle, \
                         fontsize=GRID_SIZE, color="green", owidth=1)
    else:
        screen.draw.text("You Lost!!!", midtop=screen_middle, \
                         fontsize=GRID_SIZE, color="purple", owidth=1)
        
    screen.draw.text("Press that ***** big BUTTON ON YOUR KEYBOARD!!!!!!!!!!", midtop=(WIDTH / 2, \
                     HEIGHT / 2 + GRID_SIZE), fontsize=GRID_SIZE / 2, \
                     color="red", owidth=1)
                     
def draw ():
    draw_background()
    draw_scenery()
    draw_actors()
    if game_over:
        draw_game_over()
def on_key_up(key):
    if key == keys.SPACE and game_over:
        setup_game()
def on_key_down(key):
    if key == keys.LEFT:
        move_player(-1, 0)
    elif key == keys.UP:
        move_player(0, -1)
    elif key == keys.RIGHT:
        move_player(1, 0)
    elif key == keys.DOWN:
        move_player(0, 1)
#def repeat_player_move():
 #    if keyboard.left:
 #        move_player(-1, 0)
 #   elif keyboard.up:
 #        move_player(0, -1)
 #    elif keyboard.right:
 #        move_player(1, 0)
 #    elif keyboard.down:
 #        move_player(0, 1)
 
def move_player(dx, dy):
    global game_over, player_won
    if game_over:
        return
    (x, y) = grid_coords(player)
    x += dx
    y += dy
    square = MAP[y][x]
    if square == "W":
        return
    elif square == "D":
        if len(keys_to_collect) > 0:
            return
        else:
            game_over = True
            player_won = True
    for key in keys_to_collect:
        (key_x, key_y) = grid_coords(key)
        if x == key_x and y == key_y:
            keys_to_collect.remove(key)
            break
    animate(player, pos=screen_coords(x, y), \
            duration=PLAYER_MOVE_INTERVAL)
 #           on_finished=repeat_player_move)

    player.pos = screen_coords(x, y) 

import heapq

def find_path(start, goal, map_):
    width, height = GRID_WIDTH, GRID_HEIGHT
    walls = set()
    for y in range(height):
        for x in range(width):
            if map_[y][x] == "W":
                walls.add((x, y))

    def neighbors(pos):
        x, y = pos
        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < width and 0 <= ny < height and (nx, ny) not in walls:
                yield (nx, ny)

    def heuristic(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    frontier = []
    heapq.heappush(frontier, (0, start))
    came_from = {start: None}
    cost_so_far = {start: 0}

    while frontier:
        _, current = heapq.heappop(frontier)
        if current == goal:
            break
        for next in neighbors(current):
            new_cost = cost_so_far[current] + 1
            if next not in cost_so_far or new_cost < cost_so_far[next]:
                cost_so_far[next] = new_cost
                priority = new_cost + heuristic(goal, next)
                heapq.heappush(frontier, (priority, next))
                came_from[next] = current

    # Reconstruct path
    path = []
    cur = goal
    while cur != start:
        if cur not in came_from:
            return []  # No path
        path.append(cur)
        cur = came_from[cur]
    path.reverse()
    return path
       
def move_guard(guard):
    global game_over
    if game_over:
        return

    player_pos = grid_coords(player)
    guard_pos = grid_coords(guard)
    path = find_path(guard_pos, player_pos, MAP)

    # Only move if a path exists and isn't already at the player
    if path:
        next_pos = path[0]
        animate(guard, pos=screen_coords(*next_pos), duration=GUARD_MOVE_INTERVAL)
        if next_pos == player_pos:
            game_over = True
def move_guards():
    for guard in guards:
        move_guard(guard)
setup_game()
clock.schedule_interval(move_guards, GUARD_MOVE_INTERVAL)
pgzrun.go()

    
