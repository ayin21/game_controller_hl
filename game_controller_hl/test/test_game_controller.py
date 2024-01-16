
import rclpy

from construct import Container, ListContainer, EnumIntegerString

from rclpy.node import Node
from rclpy.parameter import Parameter

from game_controller_hl.gamestate import GameStateStruct, TeamInfoStruct
from game_controller_hl.utils import get_parameters_from_other_node
from game_controller_hl.receiver import GameStateReceiver

from game_controller_hl_interfaces.msg import GameState


def test_get_parameters_from_other_node():
    rclpy.init()
    class MockNode(Node):
        def __init__(self):
            super().__init__('mock_node')
            self.declare_parameter('team_id', 1)
            self.declare_parameter('bot_id', 2)
    
    node = MockNode()
    params = get_parameters_from_other_node(node, 'mock_node', ['team_id', 'bot_id'])
    assert params['team_id'] == 1
    assert params['bot_id'] == 2
    node.destroy_node()
    rclpy.shutdown()


def test_game_state_receiver_select_team_by():
    player = dict(
        penalty=0,
        secs_till_unpenalized=0,
        number_of_yellow_cards=0,
        number_of_red_cards=0,
        number_of_warnings=0,
        goalkeeper=False
    )

    # Create a TeamInfoStruct as if it was a parsed game state
    team = TeamInfoStruct.build(dict(
        team_number=1,
        team_color=0,
        score=0,
        penalty_shot=0,
        single_shots=0,
        coach_sequence=0,
        coach_message='',
        coach=player,
        players=[player]*11
    ))

    # Parse the TeamInfoStruct and check if the selector works
    teams = [TeamInfoStruct.parse(team)]
    
    assert GameStateReceiver.select_team_by(lambda team: team.team_number == 1, teams).team_number == 1
    assert GameStateReceiver.select_team_by(lambda team: team.team_number == 2, teams) is None


def test_parse_gamestate():
    # Create dummy game state
    num_players = 11
    dummy_state_dict = dict(
        header=b'RGme',
        version=12,
        packet_number=0,
        players_per_team=num_players,
        game_type=0,
        game_state=0,
        first_half=False,
        kick_of_team=0,
        secondary_state=0,
        secondary_state_info=b'\x00\x00\x00\x00',
        drop_in_team=0,
        drop_in_time=0,
        seconds_remaining=0,
        secondary_seconds_remaining=0,
        teams=[dict(
            team_number=team_id,
            team_color=0,
            score=0,
            penalty_shot=0,
            single_shots=0,
            coach_sequence=0,
            coach_message='',
            coach=dict(
                penalty=0,
                secs_till_unpenalized=0,
                number_of_yellow_cards=0,
                number_of_red_cards=0,
                number_of_warnings=0,
                goalkeeper=False
            ),
            players=[dict(
                penalty=0,
                secs_till_unpenalized=0,
                number_of_yellow_cards=0,
                number_of_red_cards=0,
                number_of_warnings=0,
                goalkeeper=not bool(player_id)
            ) for player_id in range(num_players)]
        ) for team_id in range(2)]
    )

    # Create a GameStateStruct as if it was a parsed game state
    state = GameStateStruct.build(dummy_state_dict)

    # Binary representation of the GameStateStruct
    dummy_package = b'RGme\x0c\x00\x00\x0b\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    assert dummy_package == state

    # Parse the GameStateStruct and check if the values are correct
    state = GameStateStruct.parse(state)

    # Recursivly convert Container to dict
    def dictify(container):
        new_dict = dict()
        for key, value in container.items():
            if isinstance(value, Container):
                new_dict[key] = dictify(value)
            elif isinstance(value, ListContainer):
                new_dict[key] = [dictify(item) for item in value]
            elif isinstance(value, EnumIntegerString):
                new_dict[key] = int(value)
            elif key != '_io':
                new_dict[key] = value
        return new_dict

    # Check if the dict and the parsed game state are equal
    assert dictify(state) == dummy_state_dict


def test_on_new_gamestate():
    # Create dummy game state
    num_players = 11
    dummy_state_dict = dict(
        header=b'RGme',
        version=12,
        packet_number=0,
        players_per_team=num_players,
        game_type=0,
        game_state=0,
        first_half=False,
        kick_of_team=0,
        secondary_state=0,
        secondary_state_info=b'\x00\x00\x00\x00',
        drop_in_team=0,
        drop_in_time=0,
        seconds_remaining=0,
        secondary_seconds_remaining=0,
        teams=[dict(
            team_number=team_id,
            team_color=0,
            score=0,
            penalty_shot=0,
            single_shots=0,
            coach_sequence=0,
            coach_message='',
            coach=dict(
                penalty=0,
                secs_till_unpenalized=0,
                number_of_yellow_cards=0,
                number_of_red_cards=0,
                number_of_warnings=0,
                goalkeeper=False
            ),
            players=[dict(
                penalty=0,
                secs_till_unpenalized=0,
                number_of_yellow_cards=0,
                number_of_red_cards=0,
                number_of_warnings=0,
                goalkeeper=not bool(player_id)
            ) for player_id in range(num_players)]
        ) for team_id in range(2)]
    )

    # Create a GameStateStruct as if it was a parsed game state
    state = GameStateStruct.parse(GameStateStruct.build(dummy_state_dict))

    # Create the game state receiver with the team and player number parameter overwritten
    rclpy.init()
    receiver = GameStateReceiver(
        parameter_overrides=[
            Parameter('team_id', Parameter.Type.INTEGER, 1),
            Parameter('bot_id', Parameter.Type.INTEGER, 1),
            Parameter('listen_port', Parameter.Type.INTEGER, 3838),
            Parameter('answer_port', Parameter.Type.INTEGER, 3939),
            Parameter('listen_host', Parameter.Type.STRING, '0.0.0.0')
        ]
    )

    # Call the on_new_gamestate method and listen to the published game state message
    msg = receiver.build_game_state_msg(state)

    # Check if the message is correct
    assert msg.game_state == 0
    assert msg.secondary_state == 0
    assert msg.secondary_state_mode == 0
    assert msg.first_half == False
    assert msg.own_score == 0
    assert msg.rival_score == 0
    assert msg.seconds_remaining == 0
    assert msg.secondary_seconds_remaining == 0
    assert msg.has_kick_off == False
    assert msg.penalized == False
    assert msg.seconds_till_unpenalized == 0
    assert msg.secondary_state_team == 0
    assert msg.team_color == 0
    assert msg.drop_in_team == 0
    assert msg.drop_in_time == 0
    assert msg.penalty_shot == 0
    assert msg.single_shots == 0
    assert msg.coach_message == ''
    assert msg.team_mates_with_penalty == [False] * num_players
    assert msg.team_mates_with_red_card == [False] * num_players


