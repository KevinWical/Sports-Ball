#!/usr/bin/env python3
"""
Sports Emailer - Automated sports standings and game updates
Fetches NBA, NFL, MLB, and NHL data and sends formatted email updates
"""

import os
import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import json
import re
import html

class SportsEmailer:
    def __init__(self):
        self.nba_api_url = "https://www.balldontlie.io/api/v1/teams"
        self.nfl_api_url = "https://api.sportsdata.io/v3/nfl/scores/json/Standings/2024"
        
    def _clean_text(self, text):
        """Clean HTML and format text for email"""
        if not text:
            return ""
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        
        # Decode HTML entities
        text = html.unescape(text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Remove common web artifacts
        text = re.sub(r'Share this article', '', text, flags=re.IGNORECASE)
        text = re.sub(r'Follow us on', '', text, flags=re.IGNORECASE)
        text = re.sub(r'Subscribe to', '', text, flags=re.IGNORECASE)
        
        return text
    
    def format_mlb_standings(self, standings):
        """Format MLB standings for email"""
        if not standings:
            return "<h2>⚾ MLB Standings</h2><p><strong>⚠️ Data Unavailable</strong><br>MLB standings could not be retrieved at this time. This may be due to:<br>• ESPN API being temporarily unavailable<br>• Network connectivity issues<br>• Season being in progress<br><br>Please check back later for updated standings.</p>"
        
        html = "<h2>⚾ MLB Standings</h2>"
        html += f"<p><em>Last updated: {standings['last_updated']}</em></p>"
        
        # American League
        html += "<h3>American League</h3>"
        html += "<table border='1' style='border-collapse: collapse; width: 100%;'>"
        html += "<tr><th>Rank</th><th>Team</th><th>W</th><th>L</th><th>PCT</th><th>GB</th></tr>"
        
        for i, team in enumerate(standings['al'], 1):
            html += f"<tr><td>{i}</td><td>{team['name']}</td><td>{team['wins']}</td><td>{team['losses']}</td><td>{team['win_percentage']:.3f}</td><td>{team['games_back']}</td></tr>"
        
        html += "</table><br>"
        
        # National League
        html += "<h3>National League</h3>"
        html += "<table border='1' style='border-collapse: collapse; width: 100%;'>"
        html += "<tr><th>Rank</th><th>Team</th><th>W</th><th>L</th><th>PCT</th><th>GB</th></tr>"
        
        for i, team in enumerate(standings['nl'], 1):
            html += f"<tr><td>{i}</td><td>{team['name']}</td><td>{team['wins']}</td><td>{team['losses']}</td><td>{team['win_percentage']:.3f}</td><td>{team['games_back']}</td></tr>"
        
        html += "</table>"
        
        return html
    
    def format_nba_standings(self, standings):
        """Format NBA standings for email"""
        if not standings:
            return "<h2>🏀 NBA Standings</h2><p><strong>⚠️ Data Unavailable</strong><br>NBA standings could not be retrieved at this time. This may be due to:<br>• ESPN API being temporarily unavailable<br>• Network connectivity issues<br>• Season being in progress<br><br>Please check back later for updated standings.</p>"
        
        html = "<h2>🏀 NBA Standings</h2>"
        html += f"<p><em>Last updated: {standings['last_updated']}</em></p>"
        
        # Eastern Conference
        html += "<h3>Eastern Conference</h3>"
        html += "<table border='1' style='border-collapse: collapse; width: 100%;'>"
        html += "<tr><th>Rank</th><th>Team</th><th>W</th><th>L</th><th>PCT</th><th>GB</th></tr>"
        
        for i, team in enumerate(standings['east'], 1):
            html += f"<tr><td>{i}</td><td>{team['name']}</td><td>{team['wins']}</td><td>{team['losses']}</td><td>{team['win_percentage']:.3f}</td><td>{team['games_back']}</td></tr>"
        
        html += "</table><br>"
        
        # Western Conference
        html += "<h3>Western Conference</h3>"
        html += "<table border='1' style='border-collapse: collapse; width: 100%;'>"
        html += "<tr><th>Rank</th><th>Team</th><th>W</th><th>L</th><th>PCT</th><th>GB</th></tr>"
        
        for i, team in enumerate(standings['west'], 1):
            html += f"<tr><td>{i}</td><td>{team['name']}</td><td>{team['wins']}</td><td>{team['losses']}</td><td>{team['win_percentage']:.3f}</td><td>{team['games_back']}</td></tr>"
        
        html += "</table>"
        
        return html
    
    def format_recent_games(self, games, sport_name):
        """Format recent games for email"""
        if not games:
            return f"<h3>🏈 Recent {sport_name.upper()} Games</h3><p><strong>⚠️ No Recent Games Available</strong><br>Recent {sport_name} games could not be retrieved at this time. This may be due to:<br>• No games played in the last 7 days<br>• ESPN API being temporarily unavailable<br>• Season being in progress<br><br>Please check back later for updated game results.</p>"
        
        html = f"<h3>🏈 Recent {sport_name.upper()} Games</h3>"
        html += "<table border='1' style='border-collapse: collapse; width: 100%; margin-bottom: 20px;'>"
        html += "<tr><th>Date</th><th>Matchup</th><th>Score</th><th>Winner</th></tr>"
        
        for game in games[:10]:  # Show last 10 games
            # Format date
            try:
                from datetime import datetime
                game_date = datetime.fromisoformat(game['date'].replace('Z', '+00:00'))
                date_str = game_date.strftime('%m/%d')
            except:
                date_str = "Recent"
            
            # Format matchup and score
            matchup = f"{game['team1']} vs {game['team2']}"
            score = f"{game['score1']} - {game['score2']}"
            
            # Highlight winner
            winner = game.get('winner', '')
            if winner:
                winner_cell = f"<strong>{winner}</strong>"
            else:
                winner_cell = "TBD"
            
            html += f"<tr><td>{date_str}</td><td>{matchup}</td><td>{score}</td><td>{winner_cell}</td></tr>"
        
        html += "</table>"
        
        # Add highlights for recent games
        games_with_highlights = [g for g in games if 'highlights' in g and g['highlights']]
        if games_with_highlights:
            html += "<h4>🎯 Game Highlights</h4>"
            for game in games_with_highlights:
                html += f"<p><strong>{game['team1']} vs {game['team2']}</strong></p>"
                html += "<ul>"
                for highlight in game['highlights']:
                    html += f"<li><strong>{highlight['title']}:</strong> {highlight['description']}</li>"
                html += "</ul>"
        
        # Add boxscore data for NFL games
        if sport_name.upper() == 'NFL':
            games_with_boxscore = [g for g in games if 'boxscore' in g and g['boxscore']]
            if games_with_boxscore:
                html += "<h4>📊 Game Boxscores</h4>"
                for game in games_with_boxscore:
                    html += self._format_nfl_boxscore(game)
        
        return html
    
    def format_nfl_standings(self, standings):
        """Format NFL standings for email"""
        if not standings:
            return "<h2>🏈 NFL Standings</h2><p><strong>⚠️ Data Unavailable</strong><br>NFL standings could not be retrieved at this time. This may be due to:<br>• ESPN API being temporarily unavailable<br>• Network connectivity issues<br>• Season being in progress<br><br>Please check back later for updated standings.</p>"
        
        html = "<h2>🏈 NFL Standings</h2>"
        html += f"<p><em>Last updated: {standings['last_updated']}</em></p>"
        
        # AFC
        html += "<h3>AFC (American Football Conference)</h3>"
        html += "<table border='1' style='border-collapse: collapse; width: 100%;'>"
        html += "<tr><th>Rank</th><th>Team</th><th>W</th><th>L</th><th>T</th><th>PCT</th></tr>"
        
        for i, team in enumerate(standings['afc'], 1):
            html += f"<tr><td>{i}</td><td>{team['name']}</td><td>{team['wins']}</td><td>{team['losses']}</td><td>{team['ties']}</td><td>{team['win_percentage']:.3f}</td></tr>"
        
        html += "</table><br>"
        
        # NFC
        html += "<h3>NFC (National Football Conference)</h3>"
        html += "<table border='1' style='border-collapse: collapse; width: 100%;'>"
        html += "<tr><th>Rank</th><th>Team</th><th>W</th><th>L</th><th>T</th><th>PCT</th></tr>"
        
        for i, team in enumerate(standings['nfc'], 1):
            html += f"<tr><td>{i}</td><td>{team['name']}</td><td>{team['wins']}</td><td>{team['losses']}</td><td>{team['ties']}</td><td>{team['win_percentage']:.3f}</td></tr>"
        
        html += "</table>"
        
        return html
    
    def format_nhl_standings(self, standings):
        """Format NHL standings for email"""
        if not standings:
            return "<h2>🏒 NHL Standings</h2><p><strong>⚠️ Data Unavailable</strong><br>NHL standings could not be retrieved at this time. This may be due to:<br>• API being temporarily unavailable<br>• Network connectivity issues<br>• Season being in progress<br><br>Please check back later for updated standings.</p>"
        
        html = "<h2>🏒 NHL Standings</h2>"
        html += f"<p><em>Last updated: {standings['last_updated']}</em></p>"
        
        # Eastern Conference
        html += "<h3>Eastern Conference</h3>"
        html += "<table border='1' style='border-collapse: collapse; width: 100%;'>"
        html += "<tr><th>Rank</th><th>Team</th><th>W</th><th>L</th><th>OT</th><th>PTS</th><th>PCT</th></tr>"
        
        for i, team in enumerate(standings['east'], 1):
            html += f"<tr><td>{i}</td><td>{team['name']}</td><td>{team['wins']}</td><td>{team['losses']}</td><td>{team['overtime_losses']}</td><td>{team['points']}</td><td>{team['win_percentage']:.3f}</td></tr>"
        
        html += "</table><br>"
        
        # Western Conference
        html += "<h3>Western Conference</h3>"
        html += "<table border='1' style='border-collapse: collapse; width: 100%;'>"
        html += "<tr><th>Rank</th><th>Team</th><th>W</th><th>L</th><th>OT</th><th>PTS</th><th>PCT</th></tr>"
        
        for i, team in enumerate(standings['west'], 1):
            html += f"<tr><td>{i}</td><td>{team['name']}</td><td>{team['wins']}</td><td>{team['losses']}</td><td>{team['overtime_losses']}</td><td>{team['points']}</td><td>{team['win_percentage']:.3f}</td></tr>"
        
        html += "</table>"
        
        return html
    
    def get_nba_standings(self):
        """Fetch NBA standings from ESPN's free API"""
        try:
            # Try ESPN API first (most reliable)
            espn_data = self.get_espn_nba_standings()
            if espn_data:
                print("Successfully fetched NBA standings from ESPN API")
                return espn_data
            
            # No fallback - show error message
            print("Failed to fetch NBA standings from ESPN API")
            return None
            
        except Exception as e:
            print(f"Error fetching NBA data: {e}")
            return None
    
    def get_espn_nfl_standings(self):
        """Get NFL standings from ESPN's free API"""
        try:
            # ESPN API endpoint for NFL standings (using the xhr endpoint)
            url = "https://cdn.espn.com/core/nfl/standings?xhr=1"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            
            afc_teams = []
            nfc_teams = []
            
            print(f"ESPN API Response keys: {list(data.keys())}")
            
            # Parse the ESPN API response - the structure might be different
            if 'content' in data:
                content = data['content']
                print(f"Content keys: {list(content.keys()) if isinstance(content, dict) else 'Not a dict'}")
                
                if 'standings' in content:
                    standings = content['standings']
                    print(f"Standings type: {type(standings)}")
                    
                    # Handle different possible structures
                    if isinstance(standings, list):
                        for group in standings:
                            print(f"Group keys: {list(group.keys()) if isinstance(group, dict) else 'Not a dict'}")
                            if isinstance(group, dict) and 'groups' in group:
                                for subgroup in group['groups']:
                                    self._parse_standings_group(subgroup, afc_teams, nfc_teams)
                    elif isinstance(standings, dict):
                        if 'groups' in standings:
                            for group in standings['groups']:
                                # NFL has nested groups structure
                                if 'groups' in group:
                                    for subgroup in group['groups']:
                                        self._parse_standings_group(subgroup, afc_teams, nfc_teams)
                                else:
                                    self._parse_standings_group(group, afc_teams, nfc_teams)
            
            # Sort by win percentage
            afc_teams.sort(key=lambda x: x['win_percentage'], reverse=True)
            nfc_teams.sort(key=lambda x: x['win_percentage'], reverse=True)
            
            print(f"ESPN API: Found {len(afc_teams)} AFC teams and {len(nfc_teams)} NFC teams")
            
            if afc_teams or nfc_teams:
                return {
                    'afc': afc_teams,
                    'nfc': nfc_teams,
                    'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
            
            return None
            
        except Exception as e:
            print(f"Error fetching from ESPN API: {e}")
            return None
    
    def _parse_standings_group(self, group, afc_teams, nfc_teams):
        """Parse a standings group from ESPN API"""
        try:
            group_name = group.get('name', '').lower()
            print(f"Processing group: {group_name}")
            print(f"Group keys: {list(group.keys())}")
            
            if 'standings' in group:
                standings = group['standings']
                print(f"Standings type: {type(standings)}")
                
                # Handle standings as dictionary (ESPN API structure)
                if isinstance(standings, dict):
                    if 'entries' in standings:
                        entries = standings['entries']
                        print(f"Number of entries: {len(entries) if isinstance(entries, list) else 'Not a list'}")
                        
                        if isinstance(entries, list):
                            for i, entry in enumerate(entries):
                                print(f"Entry {i} keys: {list(entry.keys()) if isinstance(entry, dict) else 'Not a dict'}")
                                
                                if isinstance(entry, dict) and 'team' in entry and 'stats' in entry:
                                    team = entry['team']
                                    stats = entry['stats']
                                    
                                    print(f"Team keys: {list(team.keys())}")
                                    print(f"Stats type: {type(stats)}")
                                    
                                    # Extract team info
                                    team_name = team.get('name', '')
                                    team_location = team.get('location', '')
                                    full_name = f"{team_location} {team_name}".strip()
                                    
                                    # Extract stats
                                    wins = losses = ties = 0
                                    win_percentage = 0.0
                                    
                                    if isinstance(stats, list):
                                        for stat in stats:
                                            stat_name = stat.get('name', '')
                                            stat_value = stat.get('value', 0)
                                            
                                            if stat_name == 'wins':
                                                wins = int(float(stat_value))
                                            elif stat_name == 'losses':
                                                losses = int(float(stat_value))
                                            elif stat_name == 'ties':
                                                ties = int(float(stat_value))
                                            elif stat_name == 'winPercent':
                                                win_percentage = float(stat_value)
                                    
                                    # Determine conference from group name
                                    is_afc = 'afc' in group_name
                                    
                                    team_info = {
                                        'name': full_name,
                                        'wins': wins,
                                        'losses': losses,
                                        'ties': ties,
                                        'win_percentage': win_percentage,
                                        'conference': 'AFC' if is_afc else 'NFC',
                                        'division': group.get('name', 'Unknown')
                                    }
                                    
                                    if is_afc:
                                        afc_teams.append(team_info)
                                    else:
                                        nfc_teams.append(team_info)
                                    
                                    print(f"  Found team: {full_name} ({wins}-{losses}-{ties})")
                elif isinstance(standings, list):
                    print(f"Number of standings entries: {len(standings)}")
                    for i, entry in enumerate(standings):
                        print(f"Entry {i} keys: {list(entry.keys()) if isinstance(entry, dict) else 'Not a dict'}")
                        
                        if isinstance(entry, dict) and 'team' in entry and 'stats' in entry:
                            team = entry['team']
                            stats = entry['stats']
                            
                            print(f"Team keys: {list(team.keys())}")
                            print(f"Stats type: {type(stats)}")
                            
                            # Extract team info
                            team_name = team.get('name', '')
                            team_location = team.get('location', '')
                            full_name = f"{team_location} {team_name}".strip()
                            
                            # Extract stats
                            wins = losses = ties = 0
                            win_percentage = 0.0
                            
                            if isinstance(stats, list):
                                for stat in stats:
                                    stat_name = stat.get('name', '')
                                    stat_value = stat.get('value', 0)
                                    
                                    if stat_name == 'wins':
                                        wins = int(float(stat_value))
                                    elif stat_name == 'losses':
                                        losses = int(float(stat_value))
                                    elif stat_name == 'ties':
                                        ties = int(float(stat_value))
                                    elif stat_name == 'winPercent':
                                        win_percentage = float(stat_value)
                            
                            # Determine conference from group name
                            is_afc = 'afc' in group_name
                            
                            team_info = {
                                'name': full_name,
                                'wins': wins,
                                'losses': losses,
                                'ties': ties,
                                'win_percentage': win_percentage,
                                'conference': 'AFC' if is_afc else 'NFC',
                                'division': group.get('name', 'Unknown')
                            }
                            
                            if is_afc:
                                afc_teams.append(team_info)
                            else:
                                nfc_teams.append(team_info)
                            
                            print(f"  Found team: {full_name} ({wins}-{losses}-{ties})")
            else:
                print(f"No 'standings' key found in group")
        except Exception as e:
            print(f"Error parsing group: {e}")
            import traceback
            traceback.print_exc()
    
    def get_espn_nba_standings(self):
        """Get NBA standings from ESPN's free API"""
        try:
            # ESPN API endpoint for NBA standings (using the xhr endpoint)
            url = "https://cdn.espn.com/core/nba/standings?xhr=1"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            
            east_teams = []
            west_teams = []
            
            print(f"NBA ESPN API Response keys: {list(data.keys())}")
            
            # Parse the ESPN API response - similar structure to NFL
            if 'content' in data:
                content = data['content']
                print(f"NBA Content keys: {list(content.keys()) if isinstance(content, dict) else 'Not a dict'}")
                
                if 'standings' in content:
                    standings = content['standings']
                    print(f"NBA Standings type: {type(standings)}")
                    
                    # Handle different possible structures
                    if isinstance(standings, list):
                        for group in standings:
                            print(f"NBA Group keys: {list(group.keys()) if isinstance(group, dict) else 'Not a dict'}")
                            if isinstance(group, dict) and 'groups' in group:
                                for subgroup in group['groups']:
                                    self._parse_nba_standings_group(subgroup, east_teams, west_teams)
                    elif isinstance(standings, dict):
                        if 'groups' in standings:
                            for group in standings['groups']:
                                # NBA has direct standings structure
                                self._parse_nba_standings_group(group, east_teams, west_teams)
            
            # Sort by win percentage
            east_teams.sort(key=lambda x: x['win_percentage'], reverse=True)
            west_teams.sort(key=lambda x: x['win_percentage'], reverse=True)
            
            print(f"ESPN API: Found {len(east_teams)} East teams and {len(west_teams)} West teams")
            
            if east_teams or west_teams:
                return {
                    'east': east_teams,
                    'west': west_teams,
                    'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
            
            return None
            
        except Exception as e:
            print(f"Error fetching from ESPN API: {e}")
            return None
    
    def _parse_nba_standings_group(self, group, east_teams, west_teams):
        """Parse a NBA standings group from ESPN API"""
        try:
            group_name = group.get('name', '').lower()
            print(f"Processing NBA group: {group_name}")
            print(f"NBA Group keys: {list(group.keys())}")
            
            if 'standings' in group:
                standings = group['standings']
                print(f"NBA Standings type: {type(standings)}")
                
                # Handle standings as dictionary (ESPN API structure)
                if isinstance(standings, dict):
                    if 'entries' in standings:
                        entries = standings['entries']
                        print(f"Number of NBA entries: {len(entries) if isinstance(entries, list) else 'Not a list'}")
                        
                        if isinstance(entries, list):
                            for i, entry in enumerate(entries):
                                print(f"NBA Entry {i} keys: {list(entry.keys()) if isinstance(entry, dict) else 'Not a dict'}")
                                
                                if isinstance(entry, dict) and 'team' in entry and 'stats' in entry:
                                    team = entry['team']
                                    stats = entry['stats']
                                    
                                    print(f"NBA Team keys: {list(team.keys())}")
                                    print(f"NBA Stats type: {type(stats)}")
                                    
                                    # Extract team info
                                    team_name = team.get('name', '')
                                    team_location = team.get('location', '')
                                    full_name = f"{team_location} {team_name}".strip()
                                    
                                    # Extract stats
                                    wins = losses = 0
                                    win_percentage = 0.0
                                    games_back = 0.0
                                    
                                    if isinstance(stats, list):
                                        for stat in stats:
                                            stat_name = stat.get('name', '')
                                            stat_value = stat.get('value', 0)
                                            
                                            if stat_name == 'wins':
                                                wins = int(float(stat_value))
                                            elif stat_name == 'losses':
                                                losses = int(float(stat_value))
                                            elif stat_name == 'winPercent':
                                                win_percentage = float(stat_value)
                                            elif stat_name == 'gamesBack':
                                                games_back = float(stat_value)
                                    
                                    # Determine conference from group name
                                    is_east = 'east' in group_name
                                    
                                    team_info = {
                                        'name': full_name,
                                        'wins': wins,
                                        'losses': losses,
                                        'win_percentage': win_percentage,
                                        'games_back': games_back,
                                        'conference': 'East' if is_east else 'West'
                                    }
                                    
                                    if is_east:
                                        east_teams.append(team_info)
                                    else:
                                        west_teams.append(team_info)
                                    
                                    print(f"  Found NBA team: {full_name} ({wins}-{losses})")
                elif isinstance(standings, list):
                    print(f"Number of NBA standings entries: {len(standings)}")
                    for i, entry in enumerate(standings):
                        print(f"NBA Entry {i} keys: {list(entry.keys()) if isinstance(entry, dict) else 'Not a dict'}")
                        
                        if isinstance(entry, dict) and 'team' in entry and 'stats' in entry:
                            team = entry['team']
                            stats = entry['stats']
                            
                            print(f"NBA Team keys: {list(team.keys())}")
                            print(f"NBA Stats type: {type(stats)}")
                            
                            # Extract team info
                            team_name = team.get('name', '')
                            team_location = team.get('location', '')
                            full_name = f"{team_location} {team_name}".strip()
                            
                            # Extract stats
                            wins = losses = 0
                            win_percentage = 0.0
                            games_back = 0.0
                            
                            if isinstance(stats, list):
                                for stat in stats:
                                    stat_name = stat.get('name', '')
                                    stat_value = stat.get('value', 0)
                                    
                                    if stat_name == 'wins':
                                        wins = int(float(stat_value))
                                    elif stat_name == 'losses':
                                        losses = int(float(stat_value))
                                    elif stat_name == 'winPercent':
                                        win_percentage = float(stat_value)
                                    elif stat_name == 'gamesBack':
                                        games_back = float(stat_value)
                            
                            # Determine conference from group name
                            is_east = 'east' in group_name
                            
                            team_info = {
                                'name': full_name,
                                'wins': wins,
                                'losses': losses,
                                'win_percentage': win_percentage,
                                'games_back': games_back,
                                'conference': 'East' if is_east else 'West'
                            }
                            
                            if is_east:
                                east_teams.append(team_info)
                            else:
                                west_teams.append(team_info)
                            
                            print(f"  Found NBA team: {full_name} ({wins}-{losses})")
            else:
                print(f"No 'standings' key found in NBA group")
        except Exception as e:
            print(f"Error parsing NBA group: {e}")
            import traceback
            traceback.print_exc()
    

    
    def get_nfl_standings(self):
        """Fetch NFL standings using ESPN's free API"""
        try:
            # Try ESPN API first (most reliable)
            espn_data = self.get_espn_nfl_standings()
            if espn_data:
                print("Successfully fetched NFL standings from ESPN API")
                return espn_data
            
            # No fallback - show error message
            print("Failed to fetch NFL standings from ESPN API")
            return None
            
        except Exception as e:
            print(f"Error fetching NFL standings: {e}")
            return None
    

    
    def get_espn_mlb_standings(self):
        """Get MLB standings from ESPN's free API"""
        try:
            # ESPN API endpoint for MLB standings (using the xhr endpoint)
            url = "https://cdn.espn.com/core/mlb/standings?xhr=1"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            
            al_teams = []
            nl_teams = []
            
            print(f"MLB ESPN API Response keys: {list(data.keys())}")
            
            # Parse the ESPN API response - similar structure to NBA/NFL
            if 'content' in data:
                content = data['content']
                print(f"MLB Content keys: {list(content.keys()) if isinstance(content, dict) else 'Not a dict'}")
                
                if 'standings' in content:
                    standings = content['standings']
                    print(f"MLB Standings type: {type(standings)}")
                    
                    # Handle different possible structures
                    if isinstance(standings, list):
                        for group in standings:
                            print(f"MLB Group keys: {list(group.keys()) if isinstance(group, dict) else 'Not a dict'}")
                            if isinstance(group, dict) and 'groups' in group:
                                for subgroup in group['groups']:
                                    self._parse_mlb_standings_group(subgroup, al_teams, nl_teams)
                    elif isinstance(standings, dict):
                        if 'groups' in standings:
                            for group in standings['groups']:
                                # MLB has direct standings structure
                                self._parse_mlb_standings_group(group, al_teams, nl_teams)
            
            # Sort by win percentage
            al_teams.sort(key=lambda x: x['win_percentage'], reverse=True)
            nl_teams.sort(key=lambda x: x['win_percentage'], reverse=True)
            
            print(f"ESPN API: Found {len(al_teams)} AL teams and {len(nl_teams)} NL teams")
            
            if al_teams or nl_teams:
                return {
                    'al': al_teams,
                    'nl': nl_teams,
                    'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
            
            return None
            
        except Exception as e:
            print(f"Error fetching from ESPN API: {e}")
            return None
    
    def _parse_mlb_standings_group(self, group, al_teams, nl_teams):
        """Parse a MLB standings group from ESPN API"""
        try:
            group_name = group.get('name', '').lower()
            print(f"Processing MLB group: {group_name}")
            print(f"MLB Group keys: {list(group.keys())}")
            
            if 'standings' in group:
                standings = group['standings']
                print(f"MLB Standings type: {type(standings)}")
                
                # Handle standings as dictionary (ESPN API structure)
                if isinstance(standings, dict):
                    if 'entries' in standings:
                        entries = standings['entries']
                        print(f"Number of MLB entries: {len(entries) if isinstance(entries, list) else 'Not a list'}")
                        
                        if isinstance(entries, list):
                            for i, entry in enumerate(entries):
                                print(f"MLB Entry {i} keys: {list(entry.keys()) if isinstance(entry, dict) else 'Not a dict'}")
                                
                                if isinstance(entry, dict) and 'team' in entry and 'stats' in entry:
                                    team = entry['team']
                                    stats = entry['stats']
                                    
                                    print(f"MLB Team keys: {list(team.keys())}")
                                    print(f"MLB Stats type: {type(stats)}")
                                    
                                    # Extract team info
                                    team_name = team.get('name', '')
                                    team_location = team.get('location', '')
                                    full_name = f"{team_location} {team_name}".strip()
                                    
                                    # Extract stats
                                    wins = losses = 0
                                    win_percentage = 0.0
                                    games_back = 0.0
                                    
                                    if isinstance(stats, list):
                                        for stat in stats:
                                            stat_name = stat.get('name', '')
                                            stat_value = stat.get('value', 0)
                                            
                                            if stat_name == 'wins':
                                                wins = int(float(stat_value))
                                            elif stat_name == 'losses':
                                                losses = int(float(stat_value))
                                            elif stat_name == 'winPercent':
                                                win_percentage = float(stat_value)
                                            elif stat_name == 'gamesBack':
                                                games_back = float(stat_value)
                                    
                                    # Determine league from group name
                                    is_al = 'american' in group_name or 'al' in group_name
                                    
                                    team_info = {
                                        'name': full_name,
                                        'wins': wins,
                                        'losses': losses,
                                        'win_percentage': win_percentage,
                                        'games_back': games_back,
                                        'league': 'AL' if is_al else 'NL'
                                    }
                                    
                                    if is_al:
                                        al_teams.append(team_info)
                                        print(f"  Found AL team: {full_name} ({wins}-{losses})")
                                    elif is_nl:
                                        nl_teams.append(team_info)
                                        print(f"  Found NL team: {full_name} ({wins}-{losses})")
                                    else:
                                        print(f"  Unknown league for team: {full_name}")
                elif isinstance(standings, list):
                    print(f"Number of MLB standings entries: {len(standings)}")
                    for i, entry in enumerate(standings):
                        print(f"MLB Entry {i} keys: {list(entry.keys()) if isinstance(entry, dict) else 'Not a dict'}")
                        
                        if isinstance(entry, dict) and 'team' in entry and 'stats' in entry:
                            team = entry['team']
                            stats = entry['stats']
                            
                            print(f"MLB Team keys: {list(team.keys())}")
                            print(f"MLB Stats type: {type(stats)}")
                            
                            # Extract team info
                            team_name = team.get('name', '')
                            team_location = team.get('location', '')
                            full_name = f"{team_location} {team_name}".strip()
                            
                            # Extract stats
                            wins = losses = 0
                            win_percentage = 0.0
                            games_back = 0.0
                            
                            if isinstance(stats, list):
                                for stat in stats:
                                    stat_name = stat.get('name', '')
                                    stat_value = stat.get('value', 0)
                                    
                                    if stat_name == 'wins':
                                        wins = int(float(stat_value))
                                    elif stat_name == 'losses':
                                        losses = int(float(stat_value))
                                    elif stat_name == 'winPercent':
                                        win_percentage = float(stat_value)
                                    elif stat_name == 'gamesBack':
                                        games_back = float(stat_value)
                            
                            # Determine league from group name
                            is_al = 'american' in group_name or 'al' in group_name
                            
                            team_info = {
                                'name': full_name,
                                'wins': wins,
                                'losses': losses,
                                'win_percentage': win_percentage,
                                'games_back': games_back,
                                'league': 'AL' if is_al else 'NL'
                            }
                            
                            if is_al:
                                al_teams.append(team_info)
                                print(f"  Found AL team: {full_name} ({wins}-{losses})")
                            elif is_nl:
                                nl_teams.append(team_info)
                                print(f"  Found NL team: {full_name} ({wins}-{losses})")
                            else:
                                print(f"  Unknown league for team: {full_name}")
            else:
                print(f"No 'standings' key found in MLB group")
        except Exception as e:
            print(f"Error parsing MLB group: {e}")
            import traceback
            traceback.print_exc()
    
    def get_mlb_standings(self):
        """Fetch MLB standings using multiple data sources"""
        try:
            # Try ESPN API first (most reliable)
            espn_data = self.get_espn_mlb_standings()
            if espn_data:
                print("Successfully fetched MLB standings from ESPN API")
                return espn_data
            
            # Try alternative ESPN endpoint (reverse-engineered)
            alt_espn_data = self.get_espn_mlb_standings_alt()
            if alt_espn_data:
                print("Successfully fetched MLB standings from alternative ESPN endpoint")
                return alt_espn_data
            
            # Try MLB.com API (reverse-engineered)
            mlb_data = self.get_mlb_com_standings()
            if mlb_data:
                print("Successfully fetched MLB standings from MLB.com API")
                return mlb_data
            
            # Try CBS Sports scraping
            cbs_data = self.get_cbs_mlb_standings()
            if cbs_data:
                print("Successfully fetched MLB standings from CBS Sports")
                return cbs_data
            
            # Try ESPN Scraped (direct website scraping)
            espn_scraped_data = self.get_espn_mlb_standings_scraped()
            if espn_scraped_data:
                print("Successfully fetched MLB standings from ESPN Scraped")
                return espn_scraped_data
            
            # No fallback - show error message
            print("Failed to fetch MLB standings from all available sources")
            return None
            
        except Exception as e:
            print(f"Error fetching MLB standings: {e}")
            return None
    
    def get_nhl_standings(self):
        """Fetch NHL standings using multiple data sources"""
        try:
            # Try ESPN API first (most reliable)
            espn_data = self.get_espn_nhl_standings()
            if espn_data:
                print("Successfully fetched NHL standings from ESPN API")
                return espn_data
            
            # Try NHL.com API (reverse-engineered)
            nhl_data = self.get_nhl_com_standings()
            if nhl_data:
                print("Successfully fetched NHL standings from NHL.com API")
                return nhl_data
            
            # Try CBS Sports scraping
            cbs_data = self.get_cbs_nhl_standings()
            if cbs_data:
                print("Successfully fetched NHL standings from CBS Sports")
                return cbs_data
            
            # No fallback - show error message
            print("Failed to fetch NHL standings from all available sources")
            return None
            
        except Exception as e:
            print(f"Error fetching NHL standings: {e}")
            return None
    
    def get_espn_mlb_standings_alt(self):
        """Get MLB standings from alternative ESPN endpoint (reverse-engineered)"""
        try:
            # Alternative ESPN endpoint that sometimes works better
            url = "https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/standings"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'application/json',
                'Referer': 'https://www.espn.com/mlb/standings'
            }
            
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            
            al_teams = []
            nl_teams = []
            
            print(f"Alternative ESPN MLB API Response keys: {list(data.keys())}")
            
            # Parse the alternative ESPN API response
            if 'groups' in data:
                for group in data['groups']:
                    group_name = group.get('name', '').lower()
                    print(f"Processing alternative MLB group: {group_name}")
                    
                    if 'standings' in group:
                        for entry in group['standings']:
                            if 'team' in entry and 'stats' in entry:
                                team = entry['team']
                                stats = entry['stats']
                                
                                # Extract team info
                                team_name = team.get('name', '')
                                team_location = team.get('location', '')
                                full_name = f"{team_location} {team_name}".strip()
                                
                                # Extract stats
                                wins = losses = 0
                                win_percentage = 0.0
                                games_back = 0.0
                                
                                for stat in stats:
                                    stat_name = stat.get('name', '')
                                    stat_value = stat.get('value', 0)
                                    
                                    if stat_name == 'wins':
                                        wins = int(float(stat_value))
                                    elif stat_name == 'losses':
                                        losses = int(float(stat_value))
                                    elif stat_name == 'winPercent':
                                        win_percentage = float(stat_value)
                                    elif stat_name == 'gamesBack':
                                        games_back = float(stat_value)
                                
                                # Determine league from group name
                                is_al = 'american' in group_name or 'al' in group_name
                                
                                team_info = {
                                    'name': full_name,
                                    'wins': wins,
                                    'losses': losses,
                                    'win_percentage': win_percentage,
                                    'games_back': games_back,
                                    'league': 'AL' if is_al else 'NL'
                                }
                                
                                if is_al:
                                    al_teams.append(team_info)
                                else:
                                    nl_teams.append(team_info)
                                
                                print(f"  Found MLB team: {full_name} ({wins}-{losses})")
            
            # Sort by win percentage
            al_teams.sort(key=lambda x: x['win_percentage'], reverse=True)
            nl_teams.sort(key=lambda x: x['win_percentage'], reverse=True)
            
            print(f"Alternative ESPN API: Found {len(al_teams)} AL teams and {len(nl_teams)} NL teams")
            
            if al_teams or nl_teams:
                return {
                    'al': al_teams,
                    'nl': nl_teams,
                    'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
            
            return None
            
        except Exception as e:
            print(f"Error fetching from alternative ESPN API: {e}")
            return None
    
    def get_mlb_com_standings(self):
        """Get MLB standings from MLB.com API (reverse-engineered)"""
        try:
            # MLB.com API endpoint (reverse-engineered) - Updated to 2025 season
            url = "https://statsapi.mlb.com/api/v1/standings?leagueId=103,104&season=2025&standingsTypes=regularSeason"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'application/json'
            }
            
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            
            al_teams = []
            nl_teams = []
            
            print(f"MLB.com API Response keys: {list(data.keys())}")
            
            if 'records' in data:
                for record in data['records']:
                    league = record.get('league', {})
                    league_name = league.get('name', '').lower()
                    league_id = league.get('id', 0)
                    division_name = record.get('division', {}).get('name', '').lower()
                    
                    print(f"Processing MLB.com group: {league_name} (ID: {league_id}) - {division_name}")
                    
                    # Determine league based on league ID or name
                    # League ID 103 = American League, 104 = National League
                    is_al = league_id == 103 or 'american' in league_name or 'al' in league_name
                    is_nl = league_id == 104 or 'national' in league_name or 'nl' in league_name
                    
                    if 'teamRecords' in record:
                        for team_record in record['teamRecords']:
                            team = team_record.get('team', {})
                            stats = team_record.get('leagueRecord', {})
                            
                            # Extract team info
                            team_name = team.get('name', '')
                            team_location = team.get('locationName', '')
                            full_name = f"{team_location} {team_name}".strip()
                            
                            # Extract stats
                            wins = stats.get('wins', 0)
                            losses = stats.get('losses', 0)
                            games_back = team_record.get('leagueGamesBack', 0)
                            
                            # Calculate win percentage
                            win_percentage = wins / (wins + losses) if (wins + losses) > 0 else 0
                            
                            team_info = {
                                'name': full_name,
                                'wins': wins,
                                'losses': losses,
                                'win_percentage': win_percentage,
                                'games_back': games_back,
                                'league': 'AL' if is_al else 'NL'
                            }
                            
                            if is_al:
                                al_teams.append(team_info)
                                print(f"  Found AL team: {full_name} ({wins}-{losses})")
                            elif is_nl:
                                nl_teams.append(team_info)
                                print(f"  Found NL team: {full_name} ({wins}-{losses})")
                            else:
                                print(f"  Unknown league for team: {full_name}")
            
            # Sort by win percentage
            al_teams.sort(key=lambda x: x['win_percentage'], reverse=True)
            nl_teams.sort(key=lambda x: x['win_percentage'], reverse=True)
            
            print(f"MLB.com API: Found {len(al_teams)} AL teams and {len(nl_teams)} NL teams")
            
            if al_teams or nl_teams:
                return {
                    'al': al_teams,
                    'nl': nl_teams,
                    'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
            
            return None
            
        except Exception as e:
            print(f"Error fetching from MLB.com API: {e}")
            return None
    
    def get_cbs_mlb_standings(self):
        """Get MLB standings from CBS Sports (web scraping)"""
        try:
            from bs4 import BeautifulSoup
            
            url = "https://www.cbssports.com/mlb/standings/"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            al_teams = []
            nl_teams = []
            
            # Look for standings tables
            tables = soup.find_all('table', class_='tableType-1')
            
            for table in tables:
                # Try to determine if this is AL or NL based on context
                table_text = table.get_text().lower()
                is_al = 'american' in table_text or 'al' in table_text
                is_nl = 'national' in table_text or 'nl' in table_text
                
                if not (is_al or is_nl):
                    continue
                
                rows = table.find_all('tr')[1:]  # Skip header row
                
                for row in rows:
                    cells = row.find_all('td')
                    if len(cells) >= 4:
                        try:
                            team_name = cells[1].get_text().strip()
                            wins = int(cells[2].get_text().strip())
                            losses = int(cells[3].get_text().strip())
                            
                            # Calculate win percentage
                            win_percentage = wins / (wins + losses) if (wins + losses) > 0 else 0
                            
                            # Try to get games back (might be in different column)
                            games_back = 0.0
                            if len(cells) >= 5:
                                gb_text = cells[4].get_text().strip()
                                if gb_text and gb_text != '-':
                                    try:
                                        games_back = float(gb_text)
                                    except:
                                        games_back = 0.0
                            
                            team_info = {
                                'name': team_name,
                                'wins': wins,
                                'losses': losses,
                                'win_percentage': win_percentage,
                                'games_back': games_back,
                                'league': 'AL' if is_al else 'NL'
                            }
                            
                            if is_al:
                                al_teams.append(team_info)
                            else:
                                nl_teams.append(team_info)
                            
                            print(f"  Found CBS MLB team: {team_name} ({wins}-{losses})")
                            
                        except (ValueError, IndexError) as e:
                            print(f"Error parsing CBS row: {e}")
                            continue
            
            # Sort by win percentage
            al_teams.sort(key=lambda x: x['win_percentage'], reverse=True)
            nl_teams.sort(key=lambda x: x['win_percentage'], reverse=True)
            
            print(f"CBS Sports: Found {len(al_teams)} AL teams and {len(nl_teams)} NL teams")
            
            if al_teams or nl_teams:
                return {
                    'al': al_teams,
                    'nl': nl_teams,
                    'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
            
            return None
            
        except Exception as e:
            print(f"Error fetching from CBS Sports: {e}")
            return None
    
    def get_espn_mlb_standings_scraped(self):
        """Get MLB standings by scraping ESPN's website directly"""
        try:
            try:
                from bs4 import BeautifulSoup
            except ImportError:
                print("BeautifulSoup not available, skipping ESPN scraping")
                return None
            
            url = "https://www.espn.com/mlb/standings"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            al_teams = []
            nl_teams = []
            
            # Look for standings tables - ESPN uses various table classes
            tables = soup.find_all('table')
            
            for table in tables:
                # Check if this is a standings table by looking for headers
                headers = table.find_all('th')
                if not headers:
                    continue
                
                header_text = ' '.join([h.get_text().strip() for h in headers]).lower()
                
                # Skip if this doesn't look like a standings table
                if not any(keyword in header_text for keyword in ['rank', 'team', 'w', 'l', 'pct', 'gb']):
                    continue
                
                # Determine if this is AL or NL based on context
                table_context = table.find_parent().get_text().lower() if table.find_parent() else ''
                is_al = 'american' in table_context or 'al' in table_context
                is_nl = 'national' in table_context or 'nl' in table_context
                
                # If we can't determine from context, try to infer from team names
                if not (is_al or is_nl):
                    # Look for AL/NL specific teams to determine league
                    table_text = table.get_text().lower()
                    al_indicators = ['yankees', 'red sox', 'blue jays', 'rays', 'orioles', 'white sox', 'guardians', 'tigers', 'royals', 'twins', 'astros', 'angels', 'athletics', 'mariners', 'rangers']
                    nl_indicators = ['braves', 'marlins', 'mets', 'phillies', 'nationals', 'cubs', 'reds', 'brewers', 'pirates', 'cardinals', 'diamondbacks', 'rockies', 'dodgers', 'padres', 'giants']
                    
                    al_count = sum(1 for indicator in al_indicators if indicator in table_text)
                    nl_count = sum(1 for indicator in nl_indicators if indicator in table_text)
                    
                    if al_count > nl_count:
                        is_al = True
                    elif nl_count > al_count:
                        is_nl = True
                
                if not (is_al or is_nl):
                    continue
                
                rows = table.find_all('tr')[1:]  # Skip header row
                
                for row in rows:
                    cells = row.find_all('td')
                    if len(cells) >= 4:
                        try:
                            # Extract team name (usually in the second column)
                            team_name = cells[1].get_text().strip()
                            if not team_name:
                                continue
                            
                            # Extract wins and losses
                            wins = int(cells[2].get_text().strip())
                            losses = int(cells[3].get_text().strip())
                            
                            # Calculate win percentage
                            win_percentage = wins / (wins + losses) if (wins + losses) > 0 else 0
                            
                            # Try to get games back (might be in different column)
                            games_back = 0.0
                            if len(cells) >= 5:
                                gb_text = cells[4].get_text().strip()
                                if gb_text and gb_text != '-':
                                    try:
                                        games_back = float(gb_text)
                                    except:
                                        games_back = 0.0
                            
                            team_info = {
                                'name': team_name,
                                'wins': wins,
                                'losses': losses,
                                'win_percentage': win_percentage,
                                'games_back': games_back,
                                'league': 'AL' if is_al else 'NL'
                            }
                            
                            if is_al:
                                al_teams.append(team_info)
                            else:
                                nl_teams.append(team_info)
                            
                            print(f"  Found ESPN scraped MLB team: {team_name} ({wins}-{losses})")
                            
                        except (ValueError, IndexError) as e:
                            print(f"Error parsing ESPN scraped row: {e}")
                            continue
            
            # Sort by win percentage
            al_teams.sort(key=lambda x: x['win_percentage'], reverse=True)
            nl_teams.sort(key=lambda x: x['win_percentage'], reverse=True)
            
            print(f"ESPN Scraped: Found {len(al_teams)} AL teams and {len(nl_teams)} NL teams")
            
            if al_teams or nl_teams:
                return {
                    'al': al_teams,
                    'nl': nl_teams,
                    'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
            
            return None
            
        except Exception as e:
            print(f"Error scraping from ESPN website: {e}")
            return None
    
    def get_espn_nhl_standings(self):
        """Get NHL standings from ESPN's free API"""
        try:
            # ESPN API endpoint for NHL standings
            url = "https://site.api.espn.com/apis/site/v2/sports/hockey/nhl/standings"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'application/json'
            }
            
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            
            east_teams = []
            west_teams = []
            
            print(f"NHL ESPN API Response keys: {list(data.keys())}")
            
            # Parse the ESPN API response
            if 'groups' in data:
                for group in data['groups']:
                    group_name = group.get('name', '').lower()
                    print(f"Processing NHL group: {group_name}")
                    
                    if 'standings' in group:
                        for entry in group['standings']:
                            if 'team' in entry and 'stats' in entry:
                                team = entry['team']
                                stats = entry['stats']
                                
                                # Extract team info
                                team_name = team.get('name', '')
                                team_location = team.get('location', '')
                                
                                # Check if we already have a full team name
                                if team_name and team_location:
                                    # If both fields exist, check if they're the same or if one contains the other
                                    if team_name.lower() == team_location.lower():
                                        # They're the same, use just one
                                        full_name = team_name
                                    elif team_name.lower() in team_location.lower():
                                        # Name is part of location, use location
                                        full_name = team_location
                                    elif team_location.lower() in team_name.lower():
                                        # Location is part of name, use name
                                        full_name = team_name
                                    else:
                                        # They're different, combine them
                                        full_name = f"{team_location} {team_name}".strip()
                                elif team_name:
                                    # Only name exists
                                    full_name = team_name
                                elif team_location:
                                    # Only location exists
                                    full_name = team_location
                                else:
                                    # Neither exists, use a fallback
                                    full_name = "Unknown Team"
                                
                                # Extract stats
                                wins = losses = overtime_losses = points = 0
                                win_percentage = 0.0
                                
                                for stat in stats:
                                    stat_name = stat.get('name', '')
                                    stat_value = stat.get('value', 0)
                                    
                                    if stat_name == 'wins':
                                        wins = int(float(stat_value))
                                    elif stat_name == 'losses':
                                        losses = int(float(stat_value))
                                    elif stat_name == 'overtimeLosses':
                                        overtime_losses = int(float(stat_value))
                                    elif stat_name == 'points':
                                        points = int(float(stat_value))
                                    elif stat_name == 'winPercent':
                                        win_percentage = float(stat_value)
                                
                                # Determine conference from group name
                                is_east = 'east' in group_name
                                
                                team_info = {
                                    'name': full_name,
                                    'wins': wins,
                                    'losses': losses,
                                    'overtime_losses': overtime_losses,
                                    'points': points,
                                    'win_percentage': win_percentage,
                                    'conference': 'East' if is_east else 'West'
                                }
                                
                                if is_east:
                                    east_teams.append(team_info)
                                else:
                                    west_teams.append(team_info)
                                
                                print(f"  Found NHL team: {full_name} ({wins}-{losses}-{overtime_losses})")
            
            # Sort by points
            east_teams.sort(key=lambda x: x['points'], reverse=True)
            west_teams.sort(key=lambda x: x['points'], reverse=True)
            
            print(f"ESPN API: Found {len(east_teams)} East teams and {len(west_teams)} West teams")
            
            if east_teams or west_teams:
                return {
                    'east': east_teams,
                    'west': west_teams,
                    'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
            
            return None
            
        except Exception as e:
            print(f"Error fetching from ESPN API: {e}")
            return None
    
    def get_nhl_com_standings(self):
        """Get NHL standings from NHL.com API (reverse-engineered)"""
        try:
            # NHL.com API endpoint (reverse-engineered)
            url = "https://api-web.nhle.com/v1/standings/now"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'application/json'
            }
            
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            
            east_teams = []
            west_teams = []
            
            print(f"NHL.com API Response keys: {list(data.keys())}")
            
            if 'standings' in data:
                for team_data in data['standings']:
                    # Extract team info
                    team_name = team_data.get('teamName', {}).get('default', '')
                    # Use the team name directly since it's already the full name
                    full_name = team_name if team_name else "Unknown Team"
                    
                    # Extract stats
                    wins = team_data.get('wins', 0)
                    losses = team_data.get('losses', 0)
                    overtime_losses = team_data.get('otLosses', 0)
                    points = team_data.get('points', 0)
                    
                    # Calculate win percentage
                    total_games = wins + losses + overtime_losses
                    win_percentage = wins / total_games if total_games > 0 else 0
                    
                    # Determine conference
                    conference = team_data.get('conferenceName', '').lower()
                    is_east = 'east' in conference
                    
                    team_info = {
                        'name': full_name,
                        'wins': wins,
                        'losses': losses,
                        'overtime_losses': overtime_losses,
                        'points': points,
                        'win_percentage': win_percentage,
                        'conference': 'East' if is_east else 'West'
                    }
                    
                    if is_east:
                        east_teams.append(team_info)
                    else:
                        west_teams.append(team_info)
                    
                    print(f"  Found NHL.com team: {full_name} ({wins}-{losses}-{overtime_losses})")
            
            # Sort by points
            east_teams.sort(key=lambda x: x['points'], reverse=True)
            west_teams.sort(key=lambda x: x['points'], reverse=True)
            
            print(f"NHL.com API: Found {len(east_teams)} East teams and {len(west_teams)} West teams")
            
            if east_teams or west_teams:
                return {
                    'east': east_teams,
                    'west': west_teams,
                    'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
            
            return None
            
        except Exception as e:
            print(f"Error fetching from NHL.com API: {e}")
            return None
    
    def get_cbs_nhl_standings(self):
        """Get NHL standings from CBS Sports (web scraping)"""
        try:
            from bs4 import BeautifulSoup
            
            url = "https://www.cbssports.com/nhl/standings/"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            east_teams = []
            west_teams = []
            
            # Look for standings tables
            tables = soup.find_all('table', class_='tableType-1')
            
            for table in tables:
                # Try to determine if this is East or West based on context
                table_text = table.get_text().lower()
                is_east = 'east' in table_text
                is_west = 'west' in table_text
                
                if not (is_east or is_west):
                    continue
                
                rows = table.find_all('tr')[1:]  # Skip header row
                
                for row in rows:
                    cells = row.find_all('td')
                    if len(cells) >= 6:
                        try:
                            team_name = cells[1].get_text().strip()
                            wins = int(cells[2].get_text().strip())
                            losses = int(cells[3].get_text().strip())
                            overtime_losses = int(cells[4].get_text().strip())
                            points = int(cells[5].get_text().strip())
                            
                            # Calculate win percentage
                            total_games = wins + losses + overtime_losses
                            win_percentage = wins / total_games if total_games > 0 else 0
                            
                            team_info = {
                                'name': team_name,
                                'wins': wins,
                                'losses': losses,
                                'overtime_losses': overtime_losses,
                                'points': points,
                                'win_percentage': win_percentage,
                                'conference': 'East' if is_east else 'West'
                            }
                            
                            if is_east:
                                east_teams.append(team_info)
                            else:
                                west_teams.append(team_info)
                            
                            print(f"  Found CBS NHL team: {team_name} ({wins}-{losses}-{overtime_losses})")
                            
                        except (ValueError, IndexError) as e:
                            print(f"Error parsing CBS NHL row: {e}")
                            continue
            
            # Sort by points
            east_teams.sort(key=lambda x: x['points'], reverse=True)
            west_teams.sort(key=lambda x: x['points'], reverse=True)
            
            print(f"CBS Sports NHL: Found {len(east_teams)} East teams and {len(west_teams)} West teams")
            
            if east_teams or west_teams:
                return {
                    'east': east_teams,
                    'west': west_teams,
                    'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
            
            return None
            
        except Exception as e:
            print(f"Error fetching from CBS Sports NHL: {e}")
            return None
    
    def get_recent_games(self, sport='nfl', days_back=7):
        """Get recent game scores and highlights"""
        try:
            from datetime import datetime, timedelta
            
            recent_games = []
            
            # Query multiple days to get recent completed games
            for days_ago in range(1, days_back + 1):
                target_date = datetime.now() - timedelta(days=days_ago)
                date_str = target_date.strftime('%Y%m%d')
                
                if sport == 'nfl':
                    # Get NFL scoreboard for specific date
                    url = f"https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard?dates={date_str}"
                elif sport == 'mlb':
                    # Get MLB scoreboard for specific date
                    url = f"https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/scoreboard?dates={date_str}"
                elif sport == 'nhl':
                    # Get NHL scoreboard for specific date
                    url = f"https://site.api.espn.com/apis/site/v2/sports/hockey/nhl/scoreboard?dates={date_str}"
                else:  # nba
                    url = f"https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard?dates={date_str}"
                
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
                
                try:
                    response = requests.get(url, headers=headers, timeout=15)
                    response.raise_for_status()
                    
                    data = response.json()
                    
                    if 'events' in data:
                        for event in data['events']:
                            # Check if game is completed
                            status = event.get('status', {})
                            game_state = status.get('type', {}).get('state', '')
                            
                            # Only include completed games (state = 'post')
                            if game_state == 'post':
                                game_info = self._parse_game_event(event, sport)
                                if game_info:
                                    recent_games.append(game_info)
                                    print(f"Added completed game from {date_str}: {game_info['team1']} vs {game_info['team2']}")
                
                except Exception as e:
                    print(f"Error fetching games for {date_str}: {e}")
                    continue
            
            # Sort by date (most recent first)
            recent_games.sort(key=lambda x: x.get('date', ''), reverse=True)
            
            print(f"Returning {len(recent_games)} recent completed games")
            return recent_games
            
        except Exception as e:
            print(f"Error fetching recent games: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def _parse_game_event(self, event, sport):
        """Parse a game event from ESPN API"""
        try:
            # Get basic game info
            game_id = event.get('id', '')
            game_date = event.get('date', '')
            status = event.get('status', {})
            game_state = status.get('type', {}).get('state', '')
            
            # Get teams and scores
            competitors = event.get('competitions', [{}])[0].get('competitors', [])
            
            if len(competitors) >= 2:
                team1 = competitors[0]
                team2 = competitors[1]
                
                team1_name = team1.get('team', {}).get('name', '')
                team1_location = team1.get('team', {}).get('location', '')
                team1_full = f"{team1_location} {team1_name}".strip()
                team1_score = team1.get('score', '0')
                
                team2_name = team2.get('team', {}).get('name', '')
                team2_location = team2.get('team', {}).get('location', '')
                team2_full = f"{team2_location} {team2_name}".strip()
                team2_score = team2.get('score', '0')
                
                # Determine winner
                winner = None
                if team1_score != '0' and team2_score != '0':
                    if int(team1_score) > int(team2_score):
                        winner = team1_full
                    elif int(team2_score) > int(team1_score):
                        winner = team2_full
                
                game_info = {
                    'id': game_id,
                    'date': game_date,
                    'state': game_state,
                    'team1': team1_full,
                    'team2': team2_full,
                    'score1': team1_score,
                    'score2': team2_score,
                    'winner': winner,
                    'sport': sport
                }
                
                # Get highlights if game is finished
                if game_state == 'post' and game_id:
                    highlights = self._get_game_highlights(game_id, sport)
                    if highlights:
                        game_info['highlights'] = highlights
                    
                    # Get boxscore data for NFL games
                    if sport == 'nfl':
                        boxscore = self._get_nfl_boxscore(game_id)
                        if boxscore:
                            game_info['boxscore'] = boxscore
                
                return game_info
            
            return None
            
        except Exception as e:
            print(f"Error parsing game event: {e}")
            return None
    
    def _get_game_highlights(self, game_id, sport):
        """Get highlights for a specific game"""
        try:
            if sport == 'nfl':
                url = f"https://site.api.espn.com/apis/site/v2/sports/football/nfl/summary?event={game_id}"
            elif sport == 'mlb':
                url = f"https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/summary?event={game_id}"
            elif sport == 'nhl':
                url = f"https://site.api.espn.com/apis/site/v2/sports/hockey/nhl/summary?event={game_id}"
            else:  # nba
                url = f"https://site.api.espn.com/apis/site/v2/sports/basketball/nba/summary?event={game_id}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            highlights = []
            
            # Look for highlights in various sections
            if 'highlights' in data:
                highlights_data = data['highlights']
                
                # Check if highlights_data is a list or dictionary
                if isinstance(highlights_data, list):
                    # If it's already a list, use it directly
                    highlights_list = highlights_data
                elif isinstance(highlights_data, dict):
                    # If it's a dictionary, try to get the 'highlights' key
                    highlights_list = highlights_data.get('highlights', [])
                else:
                    highlights_list = []
                
                for highlight in highlights_list:
                    if isinstance(highlight, dict):
                        title = highlight.get('headline', '')
                        description = highlight.get('description', '')
                        if title:
                            highlights.append({
                                'title': title,
                                'description': description
                            })
            
            # Also check for plays or key moments
            if 'plays' in data:
                key_plays = []
                plays_data = data['plays']
                
                # Check if plays_data is a list or dictionary
                if isinstance(plays_data, list):
                    plays_list = plays_data
                elif isinstance(plays_data, dict):
                    plays_list = plays_data.get('plays', [])
                else:
                    plays_list = []
                
                # For NFL, look for more specific play types
                nfl_keywords = ['touchdown', 'field goal', 'safety', 'interception', 'fumble', 'sack', 'pass', 'run', 'kick', 'punt', 'return', 'catch', 'turnover']
                mlb_keywords = ['home run', 'homer', 'double', 'triple', 'strikeout', 'walk', 'hit']
                nhl_keywords = ['goal', 'assist', 'penalty', 'power play', 'short handed']
                nba_keywords = ['three pointer', 'dunk', 'layup', 'free throw', 'rebound', 'assist', 'steal', 'block']
                
                # Choose keywords based on sport
                if sport == 'nfl':
                    keywords = nfl_keywords
                elif sport == 'mlb':
                    keywords = mlb_keywords
                elif sport == 'nhl':
                    keywords = nhl_keywords
                else:  # nba
                    keywords = nba_keywords
                
                for play in plays_list[-5:]:  # Last 5 plays
                    if isinstance(play, dict):
                        text = play.get('text', '')
                        if text and any(keyword in text.lower() for keyword in keywords):
                            key_plays.append(text)
                
                if key_plays:
                    highlights.append({
                        'title': 'Key Plays',
                        'description': ' | '.join(key_plays)
                    })
            
            # For NFL games, also check for scoring plays or game summary
            if sport == 'nfl' and 'scoring' in data:
                scoring_data = data['scoring']
                if isinstance(scoring_data, list):
                    scoring_plays = []
                    for score in scoring_data[-3:]:  # Last 3 scoring plays
                        if isinstance(score, dict):
                            text = score.get('text', '')
                            if text:
                                scoring_plays.append(text)
                    
                    if scoring_plays:
                        highlights.append({
                            'title': 'Scoring Plays',
                            'description': ' | '.join(scoring_plays)
                        })
            
            return highlights[:5]  # Limit to 5 highlights per game
            
        except Exception as e:
            print(f"Error fetching highlights for {sport.upper()} game {game_id}: {e}")
            return []

    def _get_nfl_boxscore(self, game_id):
        """Get detailed boxscore data for NFL games using ESPN API"""
        try:
            # Use the ESPN API endpoint for detailed game data
            url = f"https://site.api.espn.com/apis/site/v2/sports/football/nfl/summary?event={game_id}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'application/json'
            }
            
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            
            boxscore = {
                'passing': {'team1': [], 'team2': []},
                'rushing': {'team1': [], 'team2': []},
                'receiving': {'team1': [], 'team2': []},
                'team_stats': {'team1': {}, 'team2': {}}
            }
            
            # Get the correct team names from the header (same source as _parse_game_event)
            team1_name = None
            team2_name = None
            
            if 'header' in data and 'competitions' in data['header']:
                competitions = data['header']['competitions']
                if competitions and 'competitors' in competitions[0]:
                    competitors = competitions[0]['competitors']
                    if len(competitors) >= 2:
                        # Use the same logic as _parse_game_event
                        team1 = competitors[0]
                        team2 = competitors[1]
                        
                        team1_name = team1.get('team', {}).get('displayName', '')
                        team2_name = team2.get('team', {}).get('displayName', '')
                        
                        print(f"Boxscore: Using team1='{team1_name}', team2='{team2_name}' from header")
            
            # Extract team statistics from boxscore.teams
            if 'boxscore' in data and 'teams' in data['boxscore']:
                teams = data['boxscore']['teams']
                if len(teams) >= 2:
                    # Find which team in boxscore.teams corresponds to team1 and team2
                    team1_stats = {}
                    team2_stats = {}
                    
                    for team in teams:
                        team_display_name = team.get('team', {}).get('displayName', '')
                        
                        # Match by team name to determine which stats belong to which team
                        if team_display_name == team1_name:
                            # Extract team statistics for team1
                            if 'statistics' in team:
                                for stat in team['statistics']:
                                    stat_name = stat.get('name', '')
                                    stat_display = stat.get('displayValue', '0')
                                    
                                    if stat_name == 'totalYards':
                                        team1_stats['total_yards'] = stat_display if stat_display != '-' else '0'
                                    elif stat_name == 'netPassingYards':
                                        team1_stats['passing_yards'] = stat_display if stat_display != '-' else '0'
                                    elif stat_name == 'rushingYards':
                                        team1_stats['rushing_yards'] = stat_display if stat_display != '-' else '0'
                                    elif stat_name == 'turnovers':
                                        team1_stats['turnovers'] = stat_display if stat_display != '-' else '0'
                        
                        elif team_display_name == team2_name:
                            # Extract team statistics for team2
                            if 'statistics' in team:
                                for stat in team['statistics']:
                                    stat_name = stat.get('name', '')
                                    stat_display = stat.get('displayValue', '0')
                                    
                                    if stat_name == 'totalYards':
                                        team2_stats['total_yards'] = stat_display if stat_display != '-' else '0'
                                    elif stat_name == 'netPassingYards':
                                        team2_stats['passing_yards'] = stat_display if stat_display != '-' else '0'
                                    elif stat_name == 'rushingYards':
                                        team2_stats['rushing_yards'] = stat_display if stat_display != '-' else '0'
                                    elif stat_name == 'turnovers':
                                        team2_stats['turnovers'] = stat_display if stat_display != '-' else '0'
                    
                    boxscore['team_stats']['team1'] = team1_stats
                    boxscore['team_stats']['team2'] = team2_stats
            
            # Extract player statistics from boxscore.players
            if 'boxscore' in data and 'players' in data['boxscore'] and team1_name and team2_name:
                players = data['boxscore']['players']
                
                for team_data in players:
                    team_name = team_data.get('team', {}).get('displayName', '')
                    
                    # Match by team name to determine which team this is
                    if team_name == team1_name:
                        team_key = 'team1'
                    elif team_name == team2_name:
                        team_key = 'team2'
                    else:
                        # Skip if we can't match the team
                        continue
                    
                    if 'statistics' in team_data:
                        for stat_category in team_data['statistics']:
                            stat_type = stat_category.get('name', '')
                            
                            if stat_type == 'passing':
                                # Parse passing stats
                                if 'athletes' in stat_category:
                                    for athlete in stat_category['athletes']:
                                        player_name = athlete.get('athlete', {}).get('displayName', 'Unknown')
                                        stats = athlete.get('stats', [])
                                        
                                        if len(stats) >= 7:
                                            passing_stats = {
                                                'name': player_name,
                                                'completions': stats[0].split('/')[0] if '/' in str(stats[0]) else '0',
                                                'attempts': stats[0].split('/')[1] if '/' in str(stats[0]) else '0',
                                                'yards': stats[1] if stats[1] != '-' else '0',
                                                'touchdowns': stats[3] if stats[3] != '-' else '0',
                                                'interceptions': stats[4] if stats[4] != '-' else '0',
                                                'rating': stats[6] if stats[6] != '-' else '0'
                                            }
                                            boxscore['passing'][team_key].append(passing_stats)
                            
                            elif stat_type == 'rushing':
                                # Parse rushing stats
                                if 'athletes' in stat_category:
                                    for athlete in stat_category['athletes']:
                                        player_name = athlete.get('athlete', {}).get('displayName', 'Unknown')
                                        stats = athlete.get('stats', [])
                                        
                                        if len(stats) >= 5:
                                            rushing_stats = {
                                                'name': player_name,
                                                'carries': stats[0] if stats[0] != '-' else '0',
                                                'yards': stats[1] if stats[1] != '-' else '0',
                                                'avg': stats[2] if stats[2] != '-' else '0',
                                                'touchdowns': stats[3] if stats[3] != '-' else '0',
                                                'long': stats[4] if stats[4] != '-' else '0'
                                            }
                                            boxscore['rushing'][team_key].append(rushing_stats)
                            
                            elif stat_type == 'receiving':
                                # Parse receiving stats
                                if 'athletes' in stat_category:
                                    for athlete in stat_category['athletes']:
                                        player_name = athlete.get('athlete', {}).get('displayName', 'Unknown')
                                        stats = athlete.get('stats', [])
                                        
                                        if len(stats) >= 4:
                                            # Calculate average yards per reception
                                            receptions = stats[0] if stats[0] != '-' else '0'
                                            yards = stats[1] if stats[1] != '-' else '0'
                                            try:
                                                avg = round(float(yards) / float(receptions), 1) if float(receptions) > 0 else 0.0
                                            except (ValueError, ZeroDivisionError):
                                                avg = 0.0
                                            
                                            receiving_stats = {
                                                'name': player_name,
                                                'receptions': receptions,
                                                'yards': yards,
                                                'avg': str(avg),
                                                'long': stats[2] if stats[2] != '-' else '0',
                                                'touchdowns': stats[3] if stats[3] != '-' else '0'
                                            }
                                            boxscore['receiving'][team_key].append(receiving_stats)
            
            # Also check leaders data for top performers
            if 'leaders' in data and team1_name and team2_name:
                for leader_category in data['leaders']:
                    category_name = leader_category.get('name', '')
                    team_leaders = leader_category.get('leaders', [])
                    
                    if category_name == 'passingYards' and team_leaders:
                        # This is passing leaders
                        for leader in team_leaders[:3]:  # Top 3 passers
                            player_name = leader.get('athlete', {}).get('displayName', 'Unknown')
                            display_value = leader.get('displayValue', '')
                            
                            # Parse display value like "10/11, 71 YDS"
                            if ',' in display_value:
                                completions_attempts = display_value.split(',')[0]
                                yards = display_value.split(',')[1].split()[0]
                                
                                # Determine which team this player belongs to
                                team_name = leader_category.get('team', {}).get('displayName', '')
                                
                                # Match by team name to determine which team this is
                                if team_name == team1_name:
                                    team_key = 'team1'
                                elif team_name == team2_name:
                                    team_key = 'team2'
                                else:
                                    # Skip if we can't match the team
                                    continue
                                
                                # Check if we already have this player
                                existing_player = next((p for p in boxscore['passing'][team_key] if p['name'] == player_name), None)
                                if not existing_player:
                                    passing_stats = {
                                        'name': player_name,
                                        'completions': completions_attempts.split('/')[0] if '/' in completions_attempts else '0',
                                        'attempts': completions_attempts.split('/')[1] if '/' in completions_attempts else '0',
                                        'yards': yards,
                                        'touchdowns': '0',  # Not provided in leaders
                                        'interceptions': '0',  # Not provided in leaders
                                        'rating': '0'  # Not provided in leaders
                                    }
                                    boxscore['passing'][team_key].append(passing_stats)
                    
                    elif category_name == 'rushingYards' and team_leaders:
                        # This is rushing leaders
                        for leader in team_leaders[:4]:  # Top 4 rushers
                            player_name = leader.get('athlete', {}).get('displayName', 'Unknown')
                            display_value = leader.get('displayValue', '')
                            
                            # Parse display value like "12 CAR, 45 YDS"
                            if 'CAR' in display_value and 'YDS' in display_value:
                                parts = display_value.split(',')
                                carries = parts[0].split()[0]
                                yards = parts[1].split()[0]
                                
                                # Determine which team this player belongs to
                                team_name = leader_category.get('team', {}).get('displayName', '')
                                
                                # Match by team name to determine which team this is
                                if team_name == team1_name:
                                    team_key = 'team1'
                                elif team_name == team2_name:
                                    team_key = 'team2'
                                else:
                                    # Skip if we can't match the team
                                    continue
                                
                                # Check if we already have this player
                                existing_player = next((p for p in boxscore['rushing'][team_key] if p['name'] == player_name), None)
                                if not existing_player:
                                    rushing_stats = {
                                        'name': player_name,
                                        'carries': carries,
                                        'yards': yards,
                                        'avg': '0',  # Not provided in leaders
                                        'touchdowns': '0',  # Not provided in leaders
                                        'long': '0'  # Not provided in leaders
                                    }
                                    boxscore['rushing'][team_key].append(rushing_stats)
                    
                    elif category_name == 'receivingYards' and team_leaders:
                        # This is receiving leaders
                        for leader in team_leaders[:4]:  # Top 4 receivers
                            player_name = leader.get('athlete', {}).get('displayName', 'Unknown')
                            display_value = leader.get('displayValue', '')
                            
                            # Parse display value like "4 REC, 45 YDS"
                            if 'REC' in display_value and 'YDS' in display_value:
                                parts = display_value.split(',')
                                receptions = parts[0].split()[0]
                                yards = parts[1].split()[0]
                                
                                # Determine which team this player belongs to
                                team_name = leader_category.get('team', {}).get('displayName', '')
                                
                                # Match by team name to determine which team this is
                                if team_name == team1_name:
                                    team_key = 'team1'
                                elif team_name == team2_name:
                                    team_key = 'team2'
                                else:
                                    # Skip if we can't match the team
                                    continue
                                
                                # Check if we already have this player in main boxscore data
                                existing_player = next((p for p in boxscore['receiving'][team_key] if p['name'] == player_name), None)
                                if existing_player:
                                    # Use existing player data which includes targets, long, touchdowns
                                    continue
                                else:
                                    # Get long and touchdowns from main boxscore data if available
                                    long = '0'
                                    touchdowns = '0'
                                    avg = '0.0'
                                    
                                    # Look for this player in the main boxscore data to get complete stats
                                    for player_data in boxscore['receiving'][team_key]:
                                        if player_data['name'] == player_name:
                                            long = player_data.get('long', '0')
                                            touchdowns = player_data.get('touchdowns', '0')
                                            avg = player_data.get('avg', '0.0')
                                            break
                                    
                                    # Calculate average if not found in existing data
                                    if avg == '0.0':
                                        try:
                                            avg = round(float(yards) / float(receptions), 1) if float(receptions) > 0 else 0.0
                                        except (ValueError, ZeroDivisionError):
                                            avg = 0.0
                                    
                                    receiving_stats = {
                                        'name': player_name,
                                        'receptions': receptions,
                                        'yards': yards,
                                        'avg': str(avg),
                                        'long': long,
                                        'touchdowns': touchdowns
                                    }
                                    boxscore['receiving'][team_key].append(receiving_stats)
            
            return boxscore
            
        except Exception as e:
            print(f"Error fetching NFL boxscore for game {game_id}: {e}")
            return None

    def send_email(self, nba_standings, nfl_standings, mlb_standings, nhl_standings, nfl_games, nba_games, mlb_games, nhl_games):
        """Send email with standings and recent games"""
        sender_email = os.getenv('SENDER_EMAIL')
        sender_password = os.getenv('SENDER_PASSWORD')
        recipient_emails_str = os.getenv('RECIPIENT_EMAIL')
        smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        smtp_port = int(os.getenv('SMTP_PORT', '587'))
        
        if not all([sender_email, sender_password, recipient_emails_str]):
            print("Missing email configuration. Please set SENDER_EMAIL, SENDER_PASSWORD, and RECIPIENT_EMAIL environment variables.")
            return False
        
        # Parse recipient emails (support comma-separated list)
        recipient_emails = [email.strip() for email in recipient_emails_str.split(',') if email.strip()]
        
        if not recipient_emails:
            print("No valid recipient emails found. Please check your RECIPIENT_EMAIL environment variable.")
            return False
        
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"🏀🏈⚾🏒 Sports Update - {datetime.now().strftime('%B %d, %Y')}"
        msg['From'] = sender_email
        msg['To'] = ', '.join(recipient_emails)  # Join multiple recipients with commas
        
        # Create HTML content
        html_content = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                table {{ border-collapse: collapse; width: 100%; margin-bottom: 20px; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
                h2 {{ color: #333; }}
                h3 {{ color: #666; }}
                h4 {{ color: #888; }}
                .header {{ background-color: #f8f9fa; padding: 20px; border-radius: 5px; margin-bottom: 20px; }}
                .highlights {{ background-color: #fff3cd; padding: 10px; border-radius: 5px; margin: 10px 0; }}
                .winner {{ color: #28a745; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🏀🏈⚾🏒 Sports Update</h1>
                <p>Here are the latest NBA, NFL, MLB, and NHL standings and recent game results for you.</p>
                <p>Data is scraped from ESPN and CBS Sports. May contain errors.</p>
                <p><em>Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</em></p>
            </div>
            
            {self.format_nba_standings(nba_standings)}
            
            <br><hr><br>
            
            {self.format_recent_games(nba_games, 'NBA')}
            
            <br><hr><br>
            
            {self.format_nfl_standings(nfl_standings)}
            
            <br><hr><br>
            
            {self.format_recent_games(nfl_games, 'NFL')}
            
            <br><hr><br>
            
            {self.format_mlb_standings(mlb_standings)}
            
            <br><hr><br>
            
            {self.format_recent_games(mlb_games, 'MLB')}
            
            <br><hr><br>
            
            {self.format_nhl_standings(nhl_standings)}
            
            <br><hr><br>
            
            {self.format_recent_games(nhl_games, 'NHL')}
            
            <br><hr><br>
            
            <p><em>Stay safe out there! ⚓</em></p>
            <p><small>This email was automatically generated.</small></p>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(html_content, 'html'))
        
        # Send email
        try:
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg, to_addrs=recipient_emails)
            server.quit()
            print(f"Email sent successfully to {len(recipient_emails)} recipient(s): {', '.join(recipient_emails)}")
            return True
        except Exception as e:
            print(f"Error sending email: {e}")
            return False

    def _format_nfl_boxscore(self, game):
        """Format NFL boxscore data for email display"""
        try:
            boxscore = game.get('boxscore', {})
            if not boxscore:
                return ""
            
            html = f"<div style='margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; background-color: #f9f9f9;'>"
            html += f"<h5 style='margin-top: 0; color: #333;'>{game['team1']} vs {game['team2']} - Boxscore</h5>"
            
            # Team Statistics
            team_stats = boxscore.get('team_stats', {})
            if team_stats.get('team1') or team_stats.get('team2'):
                html += "<h6 style='color: #666; margin: 15px 0 10px 0;'>Team Statistics</h6>"
                html += "<table border='1' style='border-collapse: collapse; width: 100%; margin-bottom: 15px; font-size: 12px;'>"
                html += f"<tr><th style='padding: 5px; background-color: #e9ecef;'>Stat</th><th style='padding: 5px; background-color: #e9ecef;'>{game['team1']}</th><th style='padding: 5px; background-color: #e9ecef;'>{game['team2']}</th></tr>"
                
                # Total Yards
                html += "<tr><td style='padding: 5px;'><strong>Total Yards</strong></td>"
                html += f"<td style='padding: 5px; text-align: center;'>{team_stats.get('team1', {}).get('total_yards', 0)}</td>"
                html += f"<td style='padding: 5px; text-align: center;'>{team_stats.get('team2', {}).get('total_yards', 0)}</td></tr>"
                
                # Passing Yards
                html += "<tr><td style='padding: 5px;'><strong>Passing Yards</strong></td>"
                html += f"<td style='padding: 5px; text-align: center;'>{team_stats.get('team1', {}).get('passing_yards', 0)}</td>"
                html += f"<td style='padding: 5px; text-align: center;'>{team_stats.get('team2', {}).get('passing_yards', 0)}</td></tr>"
                
                # Rushing Yards
                html += "<tr><td style='padding: 5px;'><strong>Rushing Yards</strong></td>"
                html += f"<td style='padding: 5px; text-align: center;'>{team_stats.get('team1', {}).get('rushing_yards', 0)}</td>"
                html += f"<td style='padding: 5px; text-align: center;'>{team_stats.get('team2', {}).get('rushing_yards', 0)}</td></tr>"
                
                # Turnovers
                html += "<tr><td style='padding: 5px;'><strong>Turnovers</strong></td>"
                html += f"<td style='padding: 5px; text-align: center;'>{team_stats.get('team1', {}).get('turnovers', 0)}</td>"
                html += f"<td style='padding: 5px; text-align: center;'>{team_stats.get('team2', {}).get('turnovers', 0)}</td></tr>"
                
                html += "</table>"
            
            # Passing Leaders
            passing = boxscore.get('passing', {})
            if passing.get('team1') or passing.get('team2'):
                html += "<h6 style='color: #666; margin: 15px 0 10px 0;'>Passing Leaders</h6>"
                html += "<table border='1' style='border-collapse: collapse; width: 100%; margin-bottom: 15px; font-size: 12px;'>"
                html += "<tr><th style='padding: 5px; background-color: #e9ecef;'>Team</th><th style='padding: 5px; background-color: #e9ecef;'>Player</th><th style='padding: 5px; background-color: #e9ecef;'>C/A</th><th style='padding: 5px; background-color: #e9ecef;'>Yards</th><th style='padding: 5px; background-color: #e9ecef;'>TD</th><th style='padding: 5px; background-color: #e9ecef;'>INT</th><th style='padding: 5px; background-color: #e9ecef;'>Rating</th></tr>"
                
                # Team 1 passing
                for player in passing.get('team1', [])[:3]:  # Top 3 passers
                    html += f"<tr><td style='padding: 5px;'>{game['team1']}</td>"
                    html += f"<td style='padding: 5px;'>{player.get('name', 'Unknown')}</td>"
                    html += f"<td style='padding: 5px; text-align: center;'>{player.get('completions', 0)}/{player.get('attempts', 0)}</td>"
                    html += f"<td style='padding: 5px; text-align: center;'>{player.get('yards', 0)}</td>"
                    html += f"<td style='padding: 5px; text-align: center;'>{player.get('touchdowns', 0)}</td>"
                    html += f"<td style='padding: 5px; text-align: center;'>{player.get('interceptions', 0)}</td>"
                    html += f"<td style='padding: 5px; text-align: center;'>{float(player.get('rating', 0)):.1f}</td></tr>"
                
                # Team 2 passing
                for player in passing.get('team2', [])[:2]:  # Top 2 passers
                    html += f"<tr><td style='padding: 5px;'>{game['team2']}</td>"
                    html += f"<td style='padding: 5px;'>{player.get('name', 'Unknown')}</td>"
                    html += f"<td style='padding: 5px; text-align: center;'>{player.get('completions', 0)}/{player.get('attempts', 0)}</td>"
                    html += f"<td style='padding: 5px; text-align: center;'>{player.get('yards', 0)}</td>"
                    html += f"<td style='padding: 5px; text-align: center;'>{player.get('touchdowns', 0)}</td>"
                    html += f"<td style='padding: 5px; text-align: center;'>{player.get('interceptions', 0)}</td>"
                    html += f"<td style='padding: 5px; text-align: center;'>{float(player.get('rating', 0)):.1f}</td></tr>"
                
                html += "</table>"
            
            # Rushing Leaders
            rushing = boxscore.get('rushing', {})
            if rushing.get('team1') or rushing.get('team2'):
                html += "<h6 style='color: #666; margin: 15px 0 10px 0;'>Rushing Leaders</h6>"
                html += "<table border='1' style='border-collapse: collapse; width: 100%; margin-bottom: 15px; font-size: 12px;'>"
                html += "<tr><th style='padding: 5px; background-color: #e9ecef;'>Team</th><th style='padding: 5px; background-color: #e9ecef;'>Player</th><th style='padding: 5px; background-color: #e9ecef;'>Carries</th><th style='padding: 5px; background-color: #e9ecef;'>Yards</th><th style='padding: 5px; background-color: #e9ecef;'>AVG</th><th style='padding: 5px; background-color: #e9ecef;'>TD</th><th style='padding: 5px; background-color: #e9ecef;'>Long</th></tr>"
                
                # Team 1 rushing
                for player in rushing.get('team1', [])[:4]:  # Top 4 rushers
                    html += f"<tr><td style='padding: 5px;'>{game['team1']}</td>"
                    html += f"<td style='padding: 5px;'>{player.get('name', 'Unknown')}</td>"
                    html += f"<td style='padding: 5px; text-align: center;'>{player.get('carries', 0)}</td>"
                    html += f"<td style='padding: 5px; text-align: center;'>{player.get('yards', 0)}</td>"
                    html += f"<td style='padding: 5px; text-align: center;'>{player.get('avg', 0)}</td>"
                    html += f"<td style='padding: 5px; text-align: center;'>{player.get('touchdowns', 0)}</td>"
                    html += f"<td style='padding: 5px; text-align: center;'>{player.get('long', 0)}</td></tr>"
                
                # Team 2 rushing
                for player in rushing.get('team2', [])[:4]:  # Top 4 rushers
                    html += f"<tr><td style='padding: 5px;'>{game['team2']}</td>"
                    html += f"<td style='padding: 5px;'>{player.get('name', 'Unknown')}</td>"
                    html += f"<td style='padding: 5px; text-align: center;'>{player.get('carries', 0)}</td>"
                    html += f"<td style='padding: 5px; text-align: center;'>{player.get('yards', 0)}</td>"
                    html += f"<td style='padding: 5px; text-align: center;'>{player.get('avg', 0)}</td>"
                    html += f"<td style='padding: 5px; text-align: center;'>{player.get('touchdowns', 0)}</td>"
                    html += f"<td style='padding: 5px; text-align: center;'>{player.get('long', 0)}</td></tr>"
                
                html += "</table>"
            
            # Receiving Leaders
            receiving = boxscore.get('receiving', {})
            if receiving.get('team1') or receiving.get('team2'):
                html += "<h6 style='color: #666; margin: 15px 0 10px 0;'>Receiving Leaders</h6>"
                html += "<table border='1' style='border-collapse: collapse; width: 100%; margin-bottom: 15px; font-size: 12px;'>"
                html += "<tr><th style='padding: 5px; background-color: #e9ecef;'>Team</th><th style='padding: 5px; background-color: #e9ecef;'>Player</th><th style='padding: 5px; background-color: #e9ecef;'>Rec</th><th style='padding: 5px; background-color: #e9ecef;'>Yards</th><th style='padding: 5px; background-color: #e9ecef;'>AVG</th><th style='padding: 5px; background-color: #e9ecef;'>TD</th><th style='padding: 5px; background-color: #e9ecef;'>Long</th></tr>"
                
                # Team 1 receiving
                for player in receiving.get('team1', [])[:4]:  # Top 4 receivers
                    html += f"<tr><td style='padding: 5px;'>{game['team1']}</td>"
                    html += f"<td style='padding: 5px;'>{player.get('name', 'Unknown')}</td>"
                    html += f"<td style='padding: 5px; text-align: center;'>{player.get('receptions', 0)}</td>"
                    html += f"<td style='padding: 5px; text-align: center;'>{player.get('yards', 0)}</td>"
                    html += f"<td style='padding: 5px; text-align: center;'>{player.get('avg', 0)}</td>"
                    html += f"<td style='padding: 5px; text-align: center;'>{player.get('touchdowns', 0)}</td>"
                    html += f"<td style='padding: 5px; text-align: center;'>{player.get('long', 0)}</td></tr>"
                
                # Team 2 receiving
                for player in receiving.get('team2', [])[:4]:  # Top 4 receivers
                    html += f"<tr><td style='padding: 5px;'>{game['team2']}</td>"
                    html += f"<td style='padding: 5px;'>{player.get('name', 'Unknown')}</td>"
                    html += f"<td style='padding: 5px; text-align: center;'>{player.get('receptions', 0)}</td>"
                    html += f"<td style='padding: 5px; text-align: center;'>{player.get('yards', 0)}</td>"
                    html += f"<td style='padding: 5px; text-align: center;'>{player.get('avg', 0)}</td>"
                    html += f"<td style='padding: 5px; text-align: center;'>{player.get('touchdowns', 0)}</td>"
                    html += f"<td style='padding: 5px; text-align: center;'>{player.get('long', 0)}</td></tr>"
                
                html += "</table>"
            
            html += "</div>"
            return html
            
        except Exception as e:
            print(f"Error formatting NFL boxscore: {e}")
            return ""

def main():
    """Main function to fetch standings and recent games, then send email"""
    emailer = SportsEmailer()
    
    print("Fetching NBA standings...")
    nba_standings = emailer.get_nba_standings()
    
    print("Fetching NFL standings...")
    nfl_standings = emailer.get_nfl_standings()
    
    print("Fetching MLB standings...")
    mlb_standings = emailer.get_mlb_standings()
    
    print("Fetching NHL standings...")
    nhl_standings = emailer.get_nhl_standings()
    
    print("Fetching recent NFL games...")
    nfl_games = emailer.get_recent_games(sport='nfl', days_back=7)
    
    print("Fetching recent NBA games...")
    nba_games = emailer.get_recent_games(sport='nba', days_back=7)
    
    print("Fetching recent MLB games...")
    mlb_games = emailer.get_recent_games(sport='mlb', days_back=7)
    
    print("Fetching recent NHL games...")
    nhl_games = emailer.get_recent_games(sport='nhl', days_back=7)
    
    print("Sending email...")
    success = emailer.send_email(nba_standings, nfl_standings, mlb_standings, nhl_standings, nfl_games, nba_games, mlb_games, nhl_games)
    
    if success:
        print("✅ Sports update email sent successfully!")
    else:
        print("❌ Failed to send email. Check your configuration.")
        exit(1)

if __name__ == "__main__":
    main() 