#
# Vince Charming (c) 2019
#

"""
Utilities specific to gathering data regarding vehicle utilization
"""

import logging
import uuid

from dateutil import parser
from general_utils import is_valid_uuid

__author__ = 'vcharming'


class VehicleUtilization(object):
    def __init__(self):
        self.num_of_transitions = 0
        # a for autonomous
        # m for manual
        # p for parked
        # u for unknown
        # Time is in seconds
        self.total_length_s = {'a': 0, 'm': 0, 'p': 0, 'u': 0}

    def reset_stats(self):
        self.num_of_transitions = 0
        for state in self.total_length_s:
            self.total_length_s[state] = 0
        return

    def get_length_all_states_s(self):
        result = 0
        for length in self.total_length_s.itervalues():
            result += length
        return result


    def print_stats(self):
        print('\tNumber of Transitions: {}'.format(self.num_of_transitions))
        print('\tTotal Length in:')
        print('\t\tAuto:    {}'.format(self.total_length_s['a']))
        print('\t\tManual:  {}'.format(self.total_length_s['m']))
        print('\t\tParked:  {}'.format(self.total_length_s['p']))
        print('\t\tUnknown: {}'.format(self.total_length_s['u']))
        return


class User(object):
    def __init__(self, first_name, last_name=None, input_uuid=None):
        '''
        Initializes the dictionaries for the respective test
        '''
        self.first_name = first_name.lower()
        self.last_name = None

        if last_name is not None:
            self.last_name = last_name.lower()

        if input_uuid is None or not is_valid_uuid(input_uuid):
            self.user_uuid = uuid.uuid4()
        else:
            self.user_uuid = input_uuid

        self.vehicle_utilization = VehicleUtilization()

    def get_full_name(self, last_name_first=False):
        if self.last_name is None:
            full_name = self.first_name.title()
        elif last_name_first:
            full_name = "{}, {}".format(self.last_name.title(), self.first_name.title())
        else:
            full_name = "{} {}".format(self.first_name.title(), self.last_name.title())
        return full_name

    def print_user(self):
        print(self.get_full_name(last_name_first=True))
        self.vehicle_utilization.print_stats()
        return


class Team(object):
    def __init__(self, id):
        self.id = id
        # An array of Users()
        self.members = []
        self.vehicle_utilization = VehicleUtilization()

    def add_member(self, user_obj):
        for member in self.members:
            if user_obj.user_uuid == member.user_uuid:
                return
        self.members.append(user_obj)
        return

    def update_members_stats(self):
        self.vehicle_utilization.reset_stats()
        for member in self.members:
            self.vehicle_utilization.num_of_transitions += member.vehicle_utilization.num_of_transitions
            for state in self.vehicle_utilization.total_length_s:
                self.vehicle_utilization.total_length_s[state] += member.vehicle_utilization.total_length_s[state]
        return

    def print_members(self):
        for member in self.members:
            print('\t{}'.format(member.get_full_name(last_name_first=True)))
        return

    def print_team(self):
        print('Team {}'.format(self.id.title()))
        self.print_members()
        self.update_members_stats()
        self.vehicle_utilization.print_stats()
        return


class Vehicle(object):
    def __init__(self, alias):
        self.alias = alias
        self.vehicle_utilization = VehicleUtilization()

    def print_vehicle(self):
        print('VEHICLE{}'.format(self.alias.upper()))
        self.vehicle_utilization.print_stats()
        return


def is_valid_row(row):
    """
    Ensures the data in the given row matches its format requirements for that column
    :param row: An array of data. Each element within the row relates to a column
    :return: A boolean; True if all of the columns passed their respective data validation
    """

    valid_flag = True

    if len(row[0]) != 11 or row[0][:7].lower() != 'vehicle':
        error_message = 'Vehicle alias must be formated as \'VEHICLEXXXX\'.'
        valid_flag = False
    elif len(row[1]) < 1 or not (
        row[1][:1].lower() == 'a' or row[1][:1].lower() == 'm' or row[1][:1].lower() == 'p' or row[1][:1].lower() == 'u'):
        error_message = ('Vehicle activity must start with \'a\' for autonomous, '
                         '\'m\' for manual, \'p\' for parked, or \'u\' for unknown.')
        valid_flag = False
    elif row[2] == '' or row[3] == '':
        error_message = 'Start and End time are required.'
        valid_flag = False
    elif row[4] == '':
        error_message = 'User name required.'
        valid_flag = False
    elif len(row[5]) != 6 and row[5][:5].lower() != 'team ':
        error_message = 'Team Name must be formated as \'Team X\'.'
        valid_flag = False

    if valid_flag:
        try:
            start_time = parser.parse(row[2])
            end_time = parser.parse(row[3])
            if start_time >= end_time:
                error_message = 'End time must be later than the Start time.'
                valid_flag = False
        except ValueError:
            error_message = 'Start and End time must be in a valid datetime format.'
            valid_flag = False

    if not valid_flag:
        logging.error('{}'.format(error_message))
    return valid_flag


def get_avg_transition_per_min(users):
    """
    Gets the average tranistions per minute across all users
    :param users: A dictionary of User()'s
    :return: The avgerage number of tranistions per minute
    """
    # The aggregate averages. Division by 60 turns it from seconds to minutes
    agg_avg = 0
    for user in users.itervalues():
        agg_avg += user.vehicle_utilization.num_of_transitions / (user.vehicle_utilization.get_length_all_states_s() / 60)

    return agg_avg/len(users)
