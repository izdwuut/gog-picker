from configparser import ConfigParser
import os
import sys

from app.random_org import Random
from app.file import File
from app._errors import Errors
from app.args import Args


class Picker:
    settings = ConfigParser(os.environ)
    settings.read('settings.ini')
    eligible = {}
    violators = {}
    winners = {}
    random = Random(settings['random']) # from config
    messager = settings['messager'] # from config
    tag = settings['reddit']['tag']
    not_included_keywords = []
    args = Args.from_config(settings['args'])
    replied_to = None
    not_entering = []

    # return JSON
    def get_results(self):
        results = []
        prefixed = self.args.links
        profile_prefix = self.reddit.get_profile_prefix() if prefixed else ''
        if self.violators:
            violations = self._get_violations()
            results.append('Users that violate rules:{}.\n'.format(violations))
        if self.eligible:
            eligible = self.reddit.get_usernames(self.eligible.keys(), prefixed)
            results.append('Users eligible for a drawing: ' + ', '.join(eligible) + '.\n')
            not_entering = self._get_not_entering()
            results.append(not_entering)
            if len(self.winners) is 1:
                s = ''
            else:
                s = 's'
            winners = []
            for user, times in self.winners.items():
                t = ' (x{})'.format(times) if times > 1 else ''
                winners.append(user + t)
            winners = [profile_prefix + winner for winner in winners]
            results.append('Winner' + s + ': ' + ', '.join(winners) + '.')
        if results:
            results = ['Results:\n'] + results
        else:
            results.append('No eligible users.')
        return ''.join(results)

    def _get_violations(self):
        prefixed = self.args.links
        if not self.args.verbose:
            users = self.reddit.get_usernames(self.violators.keys(), prefixed)
            return ' ' + ', '.join(users)
        reasons = []
        for user, reason in self.violators.items():
            user_reason = '{} ({})'.format(user, reason)
            reasons.append(user_reason)
        users = self.reddit.get_usernames(reasons, prefixed)
        return '\n' + ',\n'.join(users)

    def pick(self):
        winners = []
        if not self.eligible:
            return
        eligible = list(self.eligible.keys())
        bot = False if self.args.url else True
        n = self.args.number
        if bot or n == 1:
            winner = self._pick_one(eligible)
            self._add_winners(winner)
            return
        if n == len(eligible):
            self._add_winners(eligible)
            return
        replacement = self.args.replacement
        if n < len(eligible):
            winners = self._pick_multiple(eligible, n, replacement)
            self._add_winners(winners)
            return
        remainder_winners = []
        if replacement:
            if self.args.all:
                winners = [*eligible]
            remainder = n - len(winners)
            remainder_winners = self._pick_multiple(eligible, remainder, replacement)
        else:
            winners = [*eligible]
        self._add_winners([*winners, *remainder_winners])

    def _add_winners(self, winners):
        if isinstance(winners, str):
            winners = [winners]
        for winner in winners:
            if winner not in self.winners:
                self.winners[winner] = 0
            self.winners[winner] += 1

    def _pick_one(self, eligible):
        return self.random.item(eligible)

    def _pick_multiple(self, eligible, n, replacement):
        eligible_len = len(eligible)
        if n > eligible_len and not replacement:
            return eligible
        return self.random.items(eligible, n, replacement)

    def add_violator(self, user, reason):
        if user in self.eligible:
            del self.eligible[user]
        self.violators[user] = reason

    def add_violators(self, users, reason):
        for user in users:
            self.add_violator(user, reason)

    def get_random_user(self):
        return self.random.item(list(self.eligible))

    @staticmethod
    def _filter_users(users: dict, meets_criteria, to_filter):
        filtered = []
        for user in users.copy():
            if meets_criteria(user, to_filter):
                users.pop(user)
                filtered.append(user)
        return filtered

    @staticmethod
    def _include_user(user, to_filter):
        return not to_filter.contains(user)

    @staticmethod
    def _exclude_user(user, to_filter):
        return to_filter.contains(user)

    def apply_filter_lists(self, users):
        to_include = File(self.settings['general']['whitelist'])
        if not to_include.contents():
            to_exclude = File(self.settings['general']['blacklist'])
            blacklisted = Picker._filter_users(users, Picker._exclude_user, to_exclude)
            self.add_violators(blacklisted, Errors.BLACKLISTED)
            to_exclude.close()
        else:
            Picker._filter_users(users, Picker._include_user, to_include)
        to_include.close()

    def set_args(self, args):
        if self._validate_args(args):
            self.args.update(args)
        else:
            sys.exit(1)

    def _validate_args(self, args):
        number_error = 'Error: invalid value of number argument (must be >= 1).'
        if args.number is not None and args.number < 1:
            print(number_error)
            return False
        if self.args.number is None or self.args.number < 1:
            print(number_error)
            return False
        return True

    # add custom messager blueprint
    def send_messages(self):
        pass

    @classmethod
    def from_args(cls, args):
        picker = cls()
        picker.set_args(args)
        return picker

    def __init__(self):
        pass


if __name__ == "__main__":
    Picker.from_cli()
