import numpy as np
import pygame
import sys
from pygame import mixer
import Buttons
import random
import math


# controls the game phase - pvai or pvp
ai_click_no = False
ai_click_easy = False
ai_click_medium = False
ai_click_hard = False
ai_click_impossible = False

ROWS = 6
COLS = 7

EMPTY = 0
WINDOW_LENGTH = 4

p1_score = 0
p2_score = 0
AI_score = 0

PLAYER_1 = 0
PLAYER_2 = 1
AI = 2

P1_token = 1
P2_token = 2
AI_token = 3

#keeps track of what player's turn is currently
turn = random.choice([PLAYER_1, PLAYER_2])

#controls the game display elements
running_status = False


menu_status_1 = True
menu_status_2 = False
menu_status_3 = False
click_diff = False
credit_scene_status = False



# to create the command line board
def create_board():
    board = np.zeros((ROWS,COLS))
    return board

#gives the cordinates where the token drops after players selects column
def drop_token(board,row,col,token):
        board[row][col] = token

#checks whether player can drop on particular column
def check_validloaction(board,col):
    return board[ROWS-1][col] == 0

#as we only take col no from player, this function determines the row in the drop_token() function
def get_next_open_row(board,col):
    for i in range(ROWS):
        if board[i][col] == 0:
            return i

#describe the winning condition (all possible cases)
def winning_move(board, token):
    #horizontal
    for col in range(COLS-3):
        for row in range(ROWS):
            if board[row][col] == token and board[row][col+1] == token and board[row][col+2] == token and board[row][col+3] == token:
                return True


    #vertical
    for col in range(COLS):
        for row in range(ROWS-3):
            if board[row][col] == token and board[row+1][col] == token and board[row+2][col] == token and board[row+3][col] == token:
                return True

    #right Diagonals
    for col in range(COLS-3):
        for row in range(ROWS-3):
            if board[row][col] == token and board[row + 1][col+1] == token and board[row + 2][col+2] == token and board[row + 3][col+3] == token:
                return True

    #left Diagonals
    for col in range(COLS-3):
        for row in range(3,ROWS):
            if board[row][col] == token and board[row - 1][col + 1] == token and board[row - 2][col + 2] == token and board[row - 3][col + 3] == token:
                return True


#draw condition, describes when there is a tie
def draw_condition(board, token):
    sum = 0
    for c in range(COLS):
        for r in range(ROWS):
            if board[r][c] != 0 and winning_move(board,token) != False:
                sum += 1
    if sum >= 42:
        return True
    else:
        return False


# code for AI level - medium
def window_eval(window,token):
    score = 0
    opp_token = P1_token
    if token == P1_token:
        opp_token = AI_token

    if window.count(token) == 4:
        score += 100
    elif window.count(token) == 3 and window.count(EMPTY) == 1:
        score += 5
    elif window.count(token) == 2 and window.count(EMPTY) == 2:
        score += 2

    if window.count(opp_token) == 3 and window.count(EMPTY) == 1:
        score -= 4

    return score



def scoring_system(board, token):
    score = 0

    #center columns
    center_column = [int(i) for i in list(board[:,COLS//2])]
    center_count = center_column.count(token)
    score += center_count*3


    # for horizontal cases
    for r in range(ROWS):
        row_array = [int(i) for i in list(board[r,:])]
        for c in range(COLS - 3):
            window = row_array[c:c+WINDOW_LENGTH]
            score += window_eval(window,token)

    # for vertical cases
    for c in range(COLS):
        col_array = [int(i) for i in list(board[:,c])]
        for r in range(ROWS-3):
            window = col_array[r:r+WINDOW_LENGTH]
            score += window_eval(window,token)

    # for +ve sloped cases
    for c in range(COLS-3):
        for r in range(ROWS-3):
            window = [board[r + i][c + i] for i in range(WINDOW_LENGTH)]
            score += window_eval(window,token)

    # for -ve sloped cases
    for c in range(COLS-3):
        for r in range(ROWS-3):
            window = [board[r + 3 - i][c + i] for i in range(WINDOW_LENGTH)]
            score += window_eval(window,token)

    return score



def all_valid_locations(board):
    valid_locations = []
    for c in range(COLS):
        if check_validloaction(board,c) == True:
            valid_locations.append(c)
    return valid_locations

def choose_best_move(board,token):
    valid_loactions = all_valid_locations(board)
    best_score = -1000
    best_col = random.choice(valid_loactions)
    for col in valid_loactions:
        row = get_next_open_row(board,col)
        temp_board = board.copy()
        drop_token(temp_board,row,col,token)
        score = scoring_system(temp_board,token)
        if score > best_score:
            best_score = score
            best_col = col
    return best_col

def is_terminal_node(board):
    if winning_move(board, P1_token) or winning_move(board, AI_token) or draw_condition(board, P1_token) or draw_condition(board, P2_token) or draw_condition(board, AI_token):
        return True

def minimax(board, depth, alpha, beta, Maximizing_Player):
    valid_locations = all_valid_locations(board)
    terminal_node = is_terminal_node(board)
    if depth == 0 or terminal_node:
        if terminal_node:
            if winning_move(board, AI_token):
                return (None, 1000000000000)
            elif winning_move(board, P1_token):
                return (None, -1000000000000)
            else: #draw condition
                return (None, 0)
        else: #depth = 0
            return (None, scoring_system(board, AI_token))
    if Maximizing_Player:
        value = -math.inf
        column = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board,col)
            temp_board = board.copy()
            drop_token(temp_board,row,col,AI_token)
            new_score = minimax(temp_board,depth - 1,alpha, beta, False)[1]
            if new_score > value:
                value = new_score
                column = col
            alpha = max(alpha,value)
            if alpha >= beta:
                break
        return column, value

    else: #minimizing player
        value = math.inf
        for col in all_valid_locations(board):
            row = get_next_open_row(board,col)
            temp_board = board.copy()
            drop_token(temp_board,row,col,P1_token)
            new_score = minimax(temp_board, depth - 1,alpha, beta, True)[1]
            if new_score < value:
                value = new_score
                column = col
            beta = min(beta,value)
            if alpha >= beta:
                break
        return column, value

#error handling, when we want to take input from command line via (keyboard), handles error on wrong types of input
#now redundant
def input_col():
    while True:
        try:
            x = int(input('select b/w 0-6: '))
            if x < 0 or x > 6:
                print('only enter from 0-6')
            else:
                return x
        except ValueError:
            print('did not enter integer')



board = create_board()


#for main infinite loop
running = True

#basics for pygame
pygame.init()

r_token = pygame.image.load('2.png')
y_token = pygame.image.load('1.png')
height_red_token = r_token.get_height()
width_red_token = r_token.get_width()
height_yellow_token = y_token.get_height()
width_yellow_token = y_token.get_width()

red_token = pygame.transform.scale(r_token,((height_red_token*1),(width_red_token*1)))
yellow_token = pygame.transform.scale(y_token,((height_yellow_token*1),(width_yellow_token*1)))



icon = pygame.image.load('connect 4 icon.png')
background = pygame.image.load('BLUE BACKGROUND 700X700.png')
drop_sound = mixer.Sound('drop 2.mp3')
win_sound = mixer.Sound('winning.mp3')
tie_sound = mixer.Sound('Tie!.wav')
button_click_sound = mixer.Sound('click_sound_1.wav')
title = pygame.image.load('CONNECT 500 X 150 (1).png')
title_height = title.get_height()
title_width = title.get_width()
title_2 = pygame.image.load('FOUR  200 X 350.png')
title_2_height = title_2.get_height()
title_2_width = title_2.get_width()

credits = pygame.image.load('credits-name.png')
f_credits = pygame.transform.scale(credits,(credits.get_width()*1.4,credits.get_height()*1.4))

unit_size = 100
height = unit_size*(ROWS+1)
width = unit_size*COLS
screen = pygame.display.set_mode((width,height))
pygame.display.set_caption('Connect 4')
pygame.display.set_icon(icon)
radius = (unit_size/2) - 5


#buttion pics
menu_1_pvp = 'PvP.png'
menu_1_pvai = 'PvAI.png'
menu_1_credits = 'Credits.png'
menu_2_resume = 'Resume.png'
menu_2_restart = 'Restart.png'
menu_2_exit = 'Exit.png'
menu_2_main_menu = 'main_menu.png'
credits_screen_back = 'back_button.png'
menu_1_exit = 'Exit.png'
menu_3_easy = 'easy.png'
menu_3_medium = 'medium.png'
menu_3_hard = 'hard.png'
menu_3_impossible = 'impossible.png'




#on menu 1
pvp_button = Buttons.button(menu_1_pvp,200,250,1)
pvAI_button = Buttons.button(menu_1_pvai,200,450,1)
credits_button = Buttons.button(menu_1_credits,535,620,0.5)
exit_button_main_menu = Buttons.button(menu_1_exit,10,620,0.5)


#on menu 2
resume_button = Buttons.button(menu_2_resume,240,40,0.7)
restart_button = Buttons.button(menu_2_restart,240,210,0.7)
exit_button = Buttons.button(menu_2_exit,240,550,0.7)
main_menu_button = Buttons.button(menu_2_main_menu,240,380,0.7)
# credits screen
back_button = Buttons.button(credits_screen_back,8,590,1)

#on menu 3
easy_button = Buttons.button(menu_3_easy,240,40,0.7)
medium_button = Buttons.button(menu_3_medium,240,210,0.7)
hard_button = Buttons.button(menu_3_hard,240,380,0.7)
impossible_button = Buttons.button(menu_3_impossible,240,550,0.7)




def show_menu_1(surface):
    global running_status
    global menu_status_1
    if menu_status_1 == True and running_status == False:
        surface.blit(background,(0,0))
        final_title = pygame.transform.scale(title,(title_width*1,title_height*1))
        final_title_2 = pygame.transform.scale(title_2, (title_2_width * 1, title_2_height * 1))
        surface.blit(final_title,(30,30))
        surface.blit(final_title_2,(490, 10))
        pvp_button.draw(surface)
        pvAI_button.draw(surface)
        credits_button.draw(surface)
        exit_button_main_menu.draw(surface)
        pygame.display.update()


def show_menu_2(surface):
    global running_status
    global menu_status_2
    if menu_status_2 == True and running_status == False and menu_status_1 == False and menu_status_3 == False:
        surface.blit(background,(0,0))
        resume_button.draw(surface)
        restart_button.draw(surface)
        exit_button.draw(surface)
        main_menu_button.draw(surface)
        pygame.display.update()

def show_menu_3(surface):
    global running_status
    global menu_status_3
    if menu_status_3 == True and running_status == False and menu_status_1 == False and menu_status_2 == False:
        surface.blit(background, (0, 0))
        easy_button.draw(surface)
        medium_button.draw(surface)
        hard_button.draw(surface)
        back_button.draw(screen)
        impossible_button.draw(surface)
        pygame.display.update()


#graphical board, joining the command line board to a GUI based board
def game_board(board):
    for c in range(COLS):
        for r in range(ROWS):
            pygame.draw.rect(screen,'blue',(c*unit_size,r*unit_size+unit_size,unit_size,unit_size))
            pygame.draw.circle(screen,'black',(c*unit_size+unit_size/2,r*unit_size+unit_size+unit_size/2),radius)
    for c in range(COLS):
        for r in range(ROWS):
            if board[r][c] == P1_token:
                screen.blit(red_token,(c * unit_size + 5, height - int(r * unit_size + unit_size - 6)))
            elif board[r][c] == P2_token or board[r][c] == AI_token:
                screen.blit(yellow_token, (c * unit_size + 5, height - int(r * unit_size + unit_size - 6)))
    pygame.display.update()

#win font, display winner
win_font = pygame.font.Font('freesansbold.ttf', 32)
def winner_display(token):
    if token == P1_token:
        display = win_font.render("PLAYER RED WINS!",True,'red')
        screen.blit(display,(0,0))
    elif token == P2_token:
        display = win_font.render("PLAYER YELLOW WINS!", True, 'yellow')
        screen.blit(display, (0, 0))
    elif token == AI_token:
        display = win_font.render("AI WINS!", True, 'yellow')
        screen.blit(display, (0, 0))

#escape font, escape restart
escape_font = pygame.font.Font('freesansbold.ttf', 20)
def Escape():
    global running_status
    show_escape = escape_font.render('Press  ESCAPE',True,'white')
    screen.blit(show_escape,(550,80))
    running_status = False

#draw font,display draw(tie)
draw_font = pygame.font.Font('freesansbold.ttf', 32)
def draw():
    global running_status
    show_draw = draw_font.render("It's a DRAW!",True,'white')
    screen.blit(show_draw,(0,0))
    running_status = False

#score font,display score
score_font = pygame.font.Font('freesansbold.ttf', 32)

def show_score(token):
    global p1_score
    global p2_score
    global AI_score
    if token == P1_token:
        p1_score += 1
    elif token == P2_token:
        p2_score += 1
    elif token == 4:
        pass
    elif token == AI_token:
        AI_score += 1


    show_score_value_1 = score_font.render('PR: '+str(p1_score),True,'red')
    show_score_value_2 = score_font.render('  PY: ' + str(p2_score), True, 'yellow')
    show_score_value_3 = score_font.render('AI: ' + str(AI_score), True, 'yellow')
    screen.blit(show_score_value_1, (520, 0))
    screen.blit(show_score_value_2, (600, 0))
    screen.blit(show_score_value_3, (440, 0))



while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE and (running_status == True or (winning_move(board, P1_token) == True or winning_move(board, P2_token) == True or winning_move(board,AI_token) or draw_condition(board,AI_token) == True or
            draw_condition(board,P1_token) == True or draw_condition(board,P2_token) == True)):
                menu_status_2 = True
                running_status = False
                show_menu_2(screen)


        show_menu_1(screen)
        if pvp_button.is_clicked() and menu_status_1 == True and running_status == False and menu_status_2 == False and credit_scene_status == False:
            ai_click_no = False
            ai_click_easy = False
            ai_click_medium = False
            ai_click_hard = False
            ai_click_impossible = False
            button_click_sound.play()
            menu_status_1 = False
            running_status = True
            click_diff = True
            turn = PLAYER_1
            Buttons.button.num = 0
            screen.fill('black')
            pygame.display.update()
            board = create_board()  # resets the command line board
            game_board(board)


        if pvAI_button.is_clicked() and menu_status_1 == True and menu_status_2 == False and credit_scene_status == False and running_status == False: #still work on this
            button_click_sound.play()
            ai_click_no = True
            menu_status_1 = False
            menu_status_2 = False
            menu_status_3 = True
            credit_scene_status = False
            click_diff = True
            show_menu_3(screen)

        if easy_button.is_clicked() and menu_status_3 == True and menu_status_1 == False and menu_status_2 == False and credit_scene_status == False and running_status == False:
            button_click_sound.play()
            click_diff = True
            ai_click_easy = True
            ai_click_medium = False
            ai_click_hard = False
            ai_click_impossible = False

            running_status = True
            menu_status_1 = False
            menu_status_2 = False
            menu_status_3 = False
            turn = random.choice([PLAYER_1,AI])
            Buttons.button.num = 0
            screen.fill('black')
            pygame.display.update()
            board = create_board()  # resets the command line board
            game_board(board)




        if medium_button.is_clicked() and menu_status_3 == True and menu_status_1 == False and menu_status_2 == False and credit_scene_status == False and running_status == False:
            button_click_sound.play()
            click_diff = True
            ai_click_medium = True
            ai_click_easy = False
            ai_click_hard = False
            ai_click_impossible = False

            running_status = True
            menu_status_1 = False
            menu_status_2 = False
            menu_status_3 = False
            turn = random.choice([PLAYER_1, AI])
            Buttons.button.num = 0
            screen.fill('black')
            pygame.display.update()
            board = create_board()  # resets the command line board
            game_board(board)


        if hard_button.is_clicked() and menu_status_3 == True and menu_status_1 == False and menu_status_2 == False and credit_scene_status == False and running_status == False:
            button_click_sound.play()
            click_diff = True
            ai_click_hard = True
            ai_click_easy = False
            ai_click_medium = False
            ai_click_impossible = False

            running_status = True
            menu_status_1 = False
            menu_status_2 = False
            menu_status_3 = False
            turn = random.choice([PLAYER_1, AI])
            Buttons.button.num = 0
            screen.fill('black')
            pygame.display.update()
            board = create_board()  # resets the command line board
            game_board(board)


        if impossible_button.is_clicked() and menu_status_3 == True and menu_status_1 == False and menu_status_2 == False and credit_scene_status == False and running_status == False:
            button_click_sound.play()
            click_diff = True
            ai_click_impossible = True
            ai_click_easy = False
            ai_click_medium = False
            ai_click_hard = False

            running_status = True
            menu_status_1 = False
            menu_status_2 = False
            menu_status_3 = False
            turn = random.choice([PLAYER_1, AI])
            Buttons.button.num = 0
            screen.fill('black')
            pygame.display.update()
            board = create_board()  # resets the command line board
            game_board(board)




        if credits_button.is_clicked() and credit_scene_status == False and running_status == False and menu_status_1 == True and menu_status_2 == False:
            button_click_sound.play()
            credit_scene_status = True
            menu_status_1 = False
            running_status = False
            screen.blit(background, (0, 0))
            screen.blit(f_credits,(0,0))
            back_button.draw(screen)
            pygame.display.update()


        if exit_button_main_menu.is_clicked() and menu_status_1 == True and menu_status_2 == False and credit_scene_status == False:
            button_click_sound.play()
            pygame.time.delay(500)
            sys.exit()

        if back_button.is_clicked() and running_status == False and menu_status_1 == False and menu_status_2 == False and (credit_scene_status == True or menu_status_3 == True):
            button_click_sound.play()
            credit_scene_status = False
            menu_status_1 = True
            menu_status_3 = False
            running_status = False
            show_menu_1(screen)

        #menu two:
        if resume_button.is_clicked() and menu_status_2 == True and running_status == False:
            button_click_sound.play()
            menu_status_1 = False
            menu_status_2 = False
            click_diff = True
            if winning_move(board, P1_token) == True or winning_move(board, P2_token) == True or winning_move(board, AI_token) or draw_condition(board, P1_token) == True or draw_condition(board, P2_token) == True:
                running_status = False
                menu_status_2 = True
            else:
                running_status = True
                game_board(board)

        if restart_button.is_clicked() and menu_status_2 == True and running_status == False:
            button_click_sound.play()
            if ai_click_no == True:
                turn = random.choice([PLAYER_1,AI])
            else:
                turn = PLAYER_1
            click_diff = True
            menu_status_1 = False
            menu_status_2 = False
            running_status = True
            screen.fill('black')
            pygame.display.update()
            board = create_board()  # resets the command line board
            game_board(board)

        if exit_button.is_clicked() and menu_status_2 == True:
            button_click_sound.play()
            pygame.time.delay(500)
            sys.exit()

        if main_menu_button.is_clicked() and menu_status_2 == True and running_status == False:
            button_click_sound.play()
            click_diff = True
            menu_status_2 = False
            menu_status_1 = True
            running_status = False
            show_menu_1(screen)

        if menu_status_1 == False and running_status == True and menu_status_2 == False and menu_status_3 == False and credit_scene_status == False:
            pygame.draw.rect(screen, 'black', (0, 0, width, unit_size))
            game_board(board)

            if event.type == pygame.MOUSEMOTION and running_status == True and menu_status_1 == False and menu_status_2 == False:
                click_diff = False
                mouse_x = event.pos[0]
                if turn == PLAYER_1:
                    screen.blit(red_token, (mouse_x - (unit_size/2), 7))
                elif turn == PLAYER_2:
                    screen.blit(yellow_token, (mouse_x - (unit_size/2), 7))
                pygame.display.update()

            if event.type == pygame.MOUSEBUTTONDOWN and running_status == True and menu_status_1 == False and menu_status_2 == False and click_diff == False:
                drop_sound.play()
                x_cord = event.pos[0]//unit_size

                if turn == PLAYER_1 and running_status == True:
                    col_1 = x_cord
                    if check_validloaction(board, col_1):
                        row = get_next_open_row(board,col_1)
                        drop_token(board,row,col_1,P1_token)
                        game_board(board)

                        if ai_click_no == True and running_status == True and menu_status_1 == False and menu_status_2 == False and credit_scene_status == False and menu_status_3 == False:
                            if ai_click_easy == True or ai_click_hard == True or ai_click_medium == True or ai_click_impossible == True:
                                turn = AI

                        else:
                            turn = PLAYER_2

                        if winning_move(board,P1_token) == True:
                            win_sound.play()
                            pygame.draw.rect(screen, 'black', (0, 0, width, unit_size))
                            show_score(P1_token)
                            winner_display(P1_token)
                            Escape()
                            pygame.display.update()

                        if draw_condition(board, P1_token) == True:
                            tie_sound.play()
                            pygame.draw.rect(screen, 'black', (0, 0, width, unit_size))
                            show_score(4)
                            draw()
                            Escape()

                    else:
                        turn = PLAYER_1


                elif turn == PLAYER_2 and running_status == True:
                    col_2 = x_cord
                    if check_validloaction(board, col_2):
                        row = get_next_open_row(board,col_2)
                        drop_token(board,row,col_2,P2_token)
                        turn = PLAYER_1
                        if winning_move(board,P2_token) == True:
                            win_sound.play()
                            pygame.draw.rect(screen, 'black', (0, 0, width, unit_size))
                            show_score(P2_token)
                            winner_display(P2_token)
                            Escape()
                            pygame.display.update()

                        if draw_condition(board, P2_token) == True:
                            pygame.draw.rect(screen, 'black', (0, 0, width, unit_size))
                            tie_sound.play()
                            show_score(4)
                            draw()
                            Escape()
                    else:
                        turn = PLAYER_2

            if turn == AI and running_status == True:
                if ai_click_easy == True:
                    col_3 = random.randint(0,COLS-1)  #-- easy mode
                if ai_click_medium == True:
                    col_3 = choose_best_move(board, AI_token) # -- medium mode
                if ai_click_hard == True:
                    col_3, minimax_score = minimax(board, 4, -math.inf, math.inf, True) #--hard mode
                if ai_click_impossible == True:
                    col_3, minimax_score = minimax(board, 6, -math.inf, math.inf, True)  # -impossible mode

                if check_validloaction(board, col_3):
                    pygame.time.wait(500)
                    row = get_next_open_row(board, col_3)
                    drop_token(board, row, col_3, AI_token)
                    drop_sound.play()
                    turn = PLAYER_1
                    if winning_move(board, AI_token) == True:
                        tie_sound.play()
                        pygame.draw.rect(screen, 'black', (0, 0, width, unit_size))
                        show_score(AI_token)
                        winner_display(AI_token)
                        Escape()
                        pygame.display.update()

                    if draw_condition(board, AI_token) == True:
                        pygame.draw.rect(screen, 'black', (0, 0, width, unit_size))
                        tie_sound.play()
                        show_score(4)
                        draw()
                        Escape()
                else:
                    turn = AI


            game_board(board)

pygame.quit()
