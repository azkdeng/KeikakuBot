import praw
import prawcore
from praw.exceptions import APIException
from configparser import ConfigParser
from time import sleep

from .config import TEST_SUBREDDIT

# Constants
LIMIT = 100
SLEEP = 60
RESPONSE = 'TL note: Keikaku means plan'

class Keikaku(object):

    def __init__(self, *args, **kwargs):
        print('Starting up bot...')
        self._load_config()
        self.replied = set()

    def _load_config(self):
        print('Loading config...')
        self.config = ConfigParser()
        self.config.read('praw.ini')
        self.reddit = praw.Reddit(
            client_id=self.config['KeikakuBot']['client_id'],
            client_secret=self.config['KeikakuBot']['client_secret'],
            user_agent=self.config['KeikakuBot']['user_agent'],
            username=self.config['KeikakuBot']['username'],
            password=self.config['KeikakuBot']['password']
        )

        print('Finished loading config.\n------------------------')

    def check(self, comment):
        """Check if comment meets requirements to reply"""
        return ((not comment.id in self.replied) and
                (not str(comment.author) == self.config['KeikakuBot']['username']) and
                ('keikaku' in comment.body.lower()))

    def run(self, subreddit):
        """Run the bot"""
        print('Running bot on subreddit %s' % subreddit)
        subreddit = self.reddit.subreddit(subreddit)

        # Main loop
        while True:
            for comment in subreddit.stream.comments():
                if self.check(comment):
                    print('Passed check')
                    print(comment.id)
                    print(comment.body.lower())
                    print('-----')
                    # Reply to the comment
                    while True:
                        try:
                            comment.reply(RESPONSE)
                            print('Successfully responded to comment - %s - adding to replied set' % comment.id)
                            self.replied.add(comment.id)
                            print(self.replied)
                            print('-----')
                            break
                        except prawcore.exceptions.RequestException:
                            print('RequestException')
                            break
                        except APIException as e:
                            if e.error_type == 'RATELIMIT':
                                print('Rate Limited...\nSleeping for %d seconds...' % SLEEP)
                                sleep(SLEEP)
                            else:
                                raise e
                        except Exception as e:
                            print('Something weird broke...\n%s' % e)
                            break

                else:
                    print('Failed check')
                    print(comment.id)
                    print(comment.body.lower())
                    print('-----')

            print('Sleeping...')
            sleep(SLEEP)

if __name__ == '__main__':
    bot = Keikaku()
    bot.run(TEST_SUBREDDIT)