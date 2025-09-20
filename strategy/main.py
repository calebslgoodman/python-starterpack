from . import *
import random



def get_strategy(team: int):
    """This function tells the engine what strategy you want your bot to use"""
    
    # team == 0 means I am on the left
    # team == 1 means I am on the right
    
    if team == 0:
        print("Hello! I am team A (on the left)")
        return Strategy(goalee_formation, ball_chase)
    else:
        print("Hello! I am team B (on the right)")
        return Strategy(goalee_formation, smart_team_strategy)
    
    # NOTE when actually submitting your bot, you probably want to have the SAME strategy for both
    # sides.

def goalee_formation(score: Score) -> List[Vec2]:
    """The engine will call this function every time the field is reset:
    either after a goal, if the ball has not moved for too long, or right before endgame"""
    
    config = get_config()
    field = config.field.bottom_right()
    
    return [
        Vec2(field.x * 0.1, field.y * 0.5),
        Vec2(field.x * 0.4, field.y * 0.4),
        Vec2(field.x * 0.4, field.y * 0.5),
        Vec2(field.x * 0.4, field.y * 0.6),
    ]

def smart_team_strategy(game: GameState) -> List[PlayerAction]:
    """Advanced strategy with distinct roles for each player."""
    
    config = get_config()
    field = config.field
    allies, _ = game.teams
    ball_pos = game.ball.pos
    ball_owner_id = game.ball_owner
    
    actions = []

    # Player 0: Goalkeeper
    goalie_pos = allies[0].pos
    goal_line = field.goal_self().x + config.goal.thickness / 2.0
    goalie_target = Vec2(goal_line, ball_pos.y)
    # Clamp goalie position to stay within the goal box height
    goalie_target.y = max(min(goalie_target.y, field.height * 0.5 + config.goal.normal_height * 0.5), 
                         field.height * 0.5 - config.goal.normal_height * 0.5)
    actions.append(PlayerAction((goalie_target - goalie_pos).normalize(), None))

    # Player 1: Defender
    defender_pos = allies[1].pos
    # If ball is in our half, chase it. Otherwise, go back to defensive formation.
    if ball_pos.x < field.width * 0.5:
        defender_target = ball_pos
    else:
        defender_target = Vec2(field.width * 0.3, field.height * 0.5)
    actions.append(PlayerAction((defender_target - defender_pos).normalize(), None))

    # Player 2: Midfielder
    midfielder_pos = allies[2].pos
    # If we have possession, support the attacker. If not, get to the center.
    if ball_owner_id is not None and game.team_of(ball_owner_id) == Team.Self:
        # Pass to the attacker if the opportunity arises
        attacker_pos = allies[3].pos
        pass_vec = (attacker_pos - midfielder_pos).normalize()
        if midfielder_pos.dist(ball_pos) < config.player.pickup_radius * 1.5:
            actions.append(PlayerAction(Vec2(0, 0), pass_vec))
            
        else:
            actions.append(PlayerAction((ball_pos - midfielder_pos).normalize(), None))
    else:
        midfielder_target = Vec2(field.width * 0.5, field.height * 0.5)
        actions.append(PlayerAction((midfielder_target - midfielder_pos).normalize(), None))

    # Player 3: Attacker
    attacker_pos = allies[3].pos
    pass_vec = None
    if ball_owner_id == allies[3].id:
        # If attacker has the ball, shoot at the goal
        pass_vec = (field.goal_other() - attacker_pos).normalize()
        actions.append(PlayerAction(Vec2(0, 0), pass_vec))
    else:
        # Attacker moves to an offensive position
        # Prioritize getting the ball in the opponent's half
        if ball_pos.x > field.width * 0.5:
            attacker_target = ball_pos
        else:
            attacker_target = Vec2(field.width * 0.7, ball_pos.y)
        actions.append(PlayerAction((attacker_target - attacker_pos).normalize(), None))
        
    return actions

def ball_chase(game: GameState) -> List[PlayerAction]:
    """Very simple strategy to chase the ball and shoot on goal"""
    
    config = get_config()
    
    # NOTE Do not worry about what side your bot is on! 
    # The engine mirrors the world for you if you are on the right, 
    # so to you, you always appear on the left.
    
    return [
        PlayerAction(
            game.ball.pos - game.players[i].pos,
            config.field.goal_other() - game.players[i].pos
        ) 
        for i in range(NUM_PLAYERS)
    ]

def do_nothing(game: GameState) -> List[PlayerAction]:
    """This strategy will do nothing :("""
    
    return [
        PlayerAction(Vec2(0, 0), None) 
        for _ in range(NUM_PLAYERS)
    ]
