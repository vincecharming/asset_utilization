#
# Vince Charming (c) 2019
#

"""
This tool is used to analyze data from a Google Sheet spreadsheet. Trends and conclusions will be deduced from it
"""

import datetime
import logging
import matplotlib.pyplot as plt
import numpy as np
import os
import pygsheets
import sys
import yaml

from dateutil import parser

# Sets up an absolute path to the python directory
DIR_PATH = os.path.dirname(os.path.join(os.getcwd(), __file__))
sys.path.append(os.path.normpath(os.path.join(DIR_PATH, '..')))
from utils.vehicle_utilization_utils import VehicleUtilization, User, Team, Vehicle, is_valid_row, get_avg_transition_per_min

__author__ = 'vcharming'

# Setup verbose logging for info, warnings, and errors
logger = logging.getLogger(__name__)
FORMAT = "[%(filename)s:%(lineno)s - %(funcName)20s() - %(levelname)-5s ] %(message)s"
logging.basicConfig(format=FORMAT)
logger.setLevel(logging.DEBUG)

try:
    FILE_PATH = os.path.dirname(os.path.abspath(__file__))
    REPORT_DIR = os.path.join(os.path.dirname(os.path.dirname(FILE_PATH)), 'reports')
    logger.info("FILE_PATH {}".format(REPORT_DIR))
    # Config directory is found relative to this file. In a real repo this would be found through an absolute
    CONFIG_DIR = os.path.join(os.path.dirname(os.path.dirname(FILE_PATH)), 'config')
    with open(os.path.join(CONFIG_DIR, 'sample_data.yml')) as sample_data_yml:
        CONFIG = yaml.load(sample_data_yml)
    # Creates a Google authorization JSON if not previously created
    authorized_gsheet = pygsheets.authorize(outh_file=os.path.join(CONFIG_DIR, 'client_secret_vcharming.json'),
                                            outh_creds_store=CONFIG_DIR)
except IOError:
    logger.error('Unable to load the configuration file.')
    raise
except Exception as e:
    raise e

# Global dictionaries. Note, these could be replaced by a SQL database
users = {}
teams = {}
vehicles = {}


def get_worksheet(sheet_url, worksheet_name):
    """
    Gets the Google worksheet from a spreadsheet
    :param sheet_url: The Google sheet url
    :param worksheet_name: The worksheet (tab) name
    :return: The worksheet object
    """
    # Attempts to open the spreadsheet by url
    try:
        g_sheet = authorized_gsheet.open_by_url(sheet_url)
    except Exception as e:
        logger.error('Unable to open spreadsheet url: {}'.format(sheet_url))
        raise Exception('Please check the spreadsheet url and try again. Error:'.format(e))

    # Attempts to open the worksheet on the specified Google Sheet
    try:
        worksheet = g_sheet.worksheet_by_title(worksheet_name)
    except pygsheets.exceptions.WorksheetNotFound:
        logger.error('Unable to open the worksheet: {}'.format(worksheet_name))
        raise

    return worksheet


def parse_data_into_dicts(data):
    """
    Parses the data into global dictionaries
    :param data: The data from the worksheet
    :return:
    """

    for row_num, row in enumerate(data, 1):
        if not is_valid_row(row):
            logger.error('Row {} is misformated. Skipping.'.format(row_num + 1))
            continue

        # a for autonomous
        # m for manual
        # p for parked
        # u for unknown
        vehicle_state = row[1][:1].lower()

        #
        # Time
        #
        # Converts string into datetime object
        start_time = parser.parse(row[2])
        end_time = parser.parse(row[3])
        delta_time = end_time - start_time

        #
        # Users
        #
        split_username = row[4].lower().split('.')
        # Accounts for no last name
        last_name = None
        if len(split_username) == 2:
            last_name = split_username[1]

        user_key = row[4].lower().replace('.', '_')
        try:
            user = users[user_key]
        except KeyError:
            # Key is not present so add to dict
            users[user_key] = User(split_username[0], last_name)
            user = users[user_key]
        # Increment dictionaries
        user.vehicle_utilization.num_of_transitions += 1
        user.vehicle_utilization.total_length_s[vehicle_state] += delta_time.total_seconds()

        #
        # Teams
        #
        # Extracts the team ID
        # E.g. Team D -> d
        team_id = row[5].split(' ')[1].lower()

        try:
            team = teams[team_id]
        except KeyError:
            # Key is not present so add to dict
            teams[team_id] = Team(team_id)
            team = teams[team_id]
        team.add_member(user)

        #
        # Vehicles
        #
        # Extracts the last 4
        # E.g. VEHICLE0008 -> 0008
        vehicle_alias = row[0][-4:].lower()

        try:
            vehicle = vehicles[vehicle_alias]
        except KeyError:
            # Key is not present so add to dict
            vehicles[vehicle_alias] = Vehicle(vehicle_alias)
            vehicle = vehicles[vehicle_alias]
        # Increment dictionaries
        vehicle.vehicle_utilization.num_of_transitions += 1
        vehicle.vehicle_utilization.total_length_s[vehicle_state] += delta_time.total_seconds()

    return


def generate_high_level_graphs(agg_vehicles):
    """
    Generates a matplotlib pie chart and stacked bar chart. High level depiction of data
    :param agg_vehicles: An VehicleUtilization object that is from aggregating all vehicles
    :return:
    """

    #
    # Pie chart of Fleet Utilization
    #
    #The slices will be ordered and plotted counter-clockwise:
    labels = ['Manual', 'Autonomous', 'Parked', 'Unknown']
    colors = ['g', 'b', 'c', 'r']
    sizes = [
        round(agg_vehicles.total_length_s['m']/agg_vehicles.get_length_all_states_s(), 1),
        round(agg_vehicles.total_length_s['a']/agg_vehicles.get_length_all_states_s(), 1),
        round(agg_vehicles.total_length_s['p']/agg_vehicles.get_length_all_states_s(), 1),
        round(agg_vehicles.total_length_s['u']/agg_vehicles.get_length_all_states_s(), 1),]
    # only explodes the 2nd slice (i.e. 'Autonomous')
    explode = (0, 0.2, 0, 0)

    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    ax1.set_title('Fleet Utilization\n')
    ax1.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%',
            shadow=True, startangle=90, colors=colors)
    # Equal aspect ratio ensures that pie is drawn as a circle
    ax1.axis('equal')

    img_file_path = os.path.join(REPORT_DIR, 'fleet_utilization_pie_chart.png')
    plt.savefig(img_file_path, bbox_inches='tight')
    plt.close(fig)

    #
    # Stacked Bar Chart of Fleet Utilization by Team
    #
    autonomous = []
    manual = []
    parked = []
    unknown = []
    team_ids = []
    vehicle_states = ['unknown', 'parked', 'manual', 'autonomous']

    for team in teams.itervalues():
        team_ids.append(team.id.title())
        agg_length_s_all_states = team.vehicle_utilization.get_length_all_states_s()
        autonomous.append(
            round((team.vehicle_utilization.total_length_s['a']/agg_length_s_all_states)*100, 1))
        manual.append(
            round((team.vehicle_utilization.total_length_s['m']/agg_length_s_all_states)*100, 1))
        parked.append(
            round((team.vehicle_utilization.total_length_s['p']/agg_length_s_all_states)*100, 1))
        unknown.append(
            round((team.vehicle_utilization.total_length_s['u']/agg_length_s_all_states)*100, 1))

    fig = plt.figure()
    axes = fig.add_subplot(111)
    index = np.arange(len(autonomous))
    width = 0.35
    # Stacking the bar charts
    p1 = axes.bar(index, autonomous, width, color='b')
    p2 = axes.bar(index, manual, width, bottom=autonomous, color='g')
    p3 = axes.bar(index, parked, width, bottom=np.array(autonomous)+np.array(manual), color='c')
    p4 = axes.bar(index, unknown, width, bottom=np.array(autonomous)+np.array(manual)+np.array(parked), color='r')
    # Lable and axis initialization
    axes.set_ylabel('Percentage of Fleet Utilization')
    axes.set_xlabel('Teams')
    axes.set_title('Fleet Utilization by Team')
    axes.set_xticks(index)
    axes.set_xticklabels(team_ids)
    axes.set_ylim(0, 101)
    # Legend order matches the order the bars are stacked
    plt.legend((p4[0], p3[0], p2[0], p1[0]), vehicle_states, loc='center left',
               bbox_to_anchor=(1, 0.5), fancybox=True, shadow=True, title="Actor Class")
    img_file_path = os.path.join(REPORT_DIR, 'fleet_utilization_by_team_stacked_bar_chart.png')
    plt.savefig(img_file_path, bbox_inches='tight')
    plt.close(fig)
    return


def generate_team_level_graphs(teams, avg_transition_per_min):
    """
    Generates matplotlib line graphs for each team showing their members performance
    :param teams: A dictionary of Team objects
    :param avg_transition_per_min: The average transition per minute for every user
    :return:
    """
    for team in teams.itervalues():
        #
        # Line Graph of Transitions per Minute for All Team Members
        #
        index = np.arange(len(team.members))
        overall_avg_arr = np.full(len(team.members), avg_transition_per_min)
        members_avg_arr = []
        members_names = []
        for member in team.members:
            members_avg_arr.append(member.vehicle_utilization.num_of_transitions / (member.vehicle_utilization.get_length_all_states_s() / 60))
            members_names.append(member.get_full_name())

        fig = plt.figure()
        axes = fig.add_subplot(111)

        axes.plot(index, overall_avg_arr, label='Overall Average', color='c', marker='o')
        axes.plot(index, members_avg_arr, label='Member Average', color='b', marker='o')

        axes.set_ylabel('Transitions/Min')
        axes.set_xlabel('Members')
        axes.set_title('Transitions per Minute for Team {}'.format(team.id.title()))
        axes.set_xticks(index)
        axes.set_xticklabels(members_names, rotation='vertical')
        axes.set_ylim(-0.1, 4.1)

        handles, labels = axes.get_legend_handles_labels()
        plt.legend(handles, labels, loc='center left',
                   bbox_to_anchor=(1, 0.5), fancybox=True, shadow=True, title="Actor Class")
        axes.grid(True)

        img_file_path = os.path.join(REPORT_DIR, 'team_{}_transitions_per_min_line_graph.png'.format(team.id.lower()))
        plt.savefig(img_file_path, bbox_inches='tight')
        plt.close(fig)
    return


def main():

    worksheet = get_worksheet(CONFIG['sheet_url'], CONFIG['worksheet_name'])

    # Skips the header row
    data = worksheet.get_all_values(include_tailing_empty=False)[1:]
    parse_data_into_dicts(data)

    for team in teams.itervalues():
        team.update_members_stats()

    agg_vehicles = VehicleUtilization()
    for vehicle in vehicles.itervalues():
        agg_vehicles.num_of_transitions += vehicle.vehicle_utilization.num_of_transitions
        for state in agg_vehicles.total_length_s:
            agg_vehicles.total_length_s[state] += vehicle.vehicle_utilization.total_length_s[state]

    generate_high_level_graphs(agg_vehicles)

    avg_transition_per_min = get_avg_transition_per_min(users)
    generate_team_level_graphs(teams, avg_transition_per_min)

if __name__ == '__main__':
    main()
