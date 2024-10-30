from model.player import Player


def calculate_pers(players: list[Player]):
    # Get League Averages for only GMAC players
    (lg_AST,
     lg_FGM,
     lg_FGA,
     lg_PTS,
     lg_FTM,
     lg_FTA,
     lg_OREB,
     lg_REB,
     lg_TOV,
     lg_PF
     ) = calculate_league_avgs([player for player in players if player.CONFERENCE])

    # Get Team Stats (AST, FGM) for all teams
    team_ast_dict, team_fgm_dict = calculate_team_stats(players)

    # Calculate factor, VOP and DRB%
    factor = 0.66 - (0.5*(lg_AST/lg_FGM)) / (2*(lg_FGM/lg_FTM))
    VOP = lg_PTS/(lg_FGA-lg_OREB+lg_TOV+(0.44*lg_FTA))
    DRB_percent = (lg_REB-lg_OREB)/lg_REB

    # Calculate every players uPER
    total_conference_players = 0
    total_conference_uPER = 0

    for player in players:
        calculate_uPER(player,
                       factor,
                       VOP,
                       DRB_percent,
                       team_ast_dict.get(player.TEAM),
                       team_fgm_dict.get(player.TEAM),
                       lg_FTM,
                       lg_FTA,
                       lg_PF
                       )

        if player.CONFERENCE:
            total_conference_players += 1
            total_conference_uPER += player.UPER

    # TODO: Adjust for each team's pace

    # Update PER attribute on every player
    lg_UPER = total_conference_uPER/total_conference_players
    print(f"Conference uPER: {total_conference_uPER} Conference Players: {total_conference_players} lg_UPER: {lg_UPER}")

    for player in players:
        player.PER = (player.UPER / lg_UPER) * 15


def calculate_league_avgs(league_players: list[Player]):
    lg_AST = sum(player.AST for player in league_players)
    lg_FGM = sum(player.FGM for player in league_players)
    lg_FGA = sum(player.FGA for player in league_players)
    lg_PTS = sum(player.PTS for player in league_players)
    lg_FTM = sum(player.FTM for player in league_players)
    lg_FTA = sum(player.FTA for player in league_players)
    lg_OREB = sum(player.OREB for player in league_players)
    lg_REB = sum(player.REB for player in league_players)
    lg_TOV = sum(player.TOV for player in league_players)
    lg_PF = sum(player.FOUL for player in league_players)

    return lg_AST, lg_FGM, lg_FGA, lg_PTS, lg_FTM, lg_FTA, lg_OREB, lg_REB, lg_TOV, lg_PF


def calculate_team_stats(players: list[Player]):
    team_ast_dict = {team: sum(player.AST for player in players if player.TEAM == team) for team in set(player.TEAM for player in players)}
    team_fgm_dict = {team: sum(player.FGM for player in players if player.TEAM == team) for team in set(player.TEAM for player in players)}

    return team_ast_dict, team_fgm_dict


# TODO: Find cleaner way to do this
def calculate_uPER(player: Player,
                   factor: float,
                   VOP: float,
                   DRB_percent: float,
                   team_ast,
                   team_fgm,
                   lg_ftm,
                   lg_fta,
                   lg_pf
                   ):

    ast_to_fgm = team_ast / team_fgm

    uPER = (1/player.MP) * (
        player.THREES 
         + 0.66*player.AST
         + (2-factor*ast_to_fgm)*player.FGM
         + (player.FTM*0.5*(1+(1-ast_to_fgm)+0.66*ast_to_fgm))
         - VOP*player.TOV
         - VOP*DRB_percent*(player.FGA-player.FGM)
         - VOP*0.44*(0.44+(0.56*DRB_percent))*(player.FTA-player.FTM)
         + VOP*(1-DRB_percent)*(player.REB-player.OREB)
         + VOP*DRB_percent*player.OREB
         + VOP*player.STL
         + VOP*DRB_percent*player.BLK
         - player.FOUL*((lg_ftm/lg_pf)-0.44*(lg_fta/lg_pf)*VOP)
        )

    player.UPER = uPER
