

import click
import re
import us

from twitter import fs
from twitter.models import StateTweet
from twitter.utils import get_spark


def match_state(tweet):
    """Probe for state.
    """
    tokens = re.findall('[a-z]+', tweet.user.location, re.I)
    tokens_lower = map(str.lower, tokens)

    for state in us.states.STATES:
        if state.abbr in tokens or state.name.lower() in tokens_lower:
            return StateTweet(state.abbr, tweet.user.location, tweet.text)


@click.command()
@click.option('--src', default='data/tweets.parquet')
@click.option('--dest', default='data/states.parquet')
def main(src, dest):
    """Get tweets for cities, using (stupid) string matching.
    """
    sc, spark = get_spark()

    tweets = spark.read.parquet(src)

    matches = tweets.rdd \
        .filter(lambda t: t.user.location and t.lang == 'en') \
        .map(match_state) \
        .filter(bool) \
        .toDF(StateTweet.schema)

    matches.write \
        .mode('overwrite') \
        .parquet(dest)

    print(matches.count())


if __name__ == '__main__':
    main()