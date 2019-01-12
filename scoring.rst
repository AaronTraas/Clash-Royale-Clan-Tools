==================================================
Clan scoring computation
==================================================

We generate a clan "score" that tells us whether to promote, demote, or kick
players. Since within the game, there's no easy way to get a full view of
everything, and there's a lot of information to keep track of, this is a
handy shorthand.

There are two primary components to the score: `War Participation`_ and
`Donations`_. These two factors are calculated seperately, and then added to
form the score. After we calculate the `Total Score`_, we then make
`Kick and Demote Recommendations`_.

There are a list of constants that can be changed in the configuration of
this application that will tweak how the scoring will be applied. These are:

MINIMUM_DONATIONS_PER_DAY
	The minimum number of donations per day each member must make on average
	to have a positive score. Default is 10.

ZERO_DONATIONS_PENALTY
    The penalty in points for having zero donations

CLAN_MINIMUM_MEMBERS
	The minimum number of members the clan wishes to maintain. This is used
	for calculating kick reccomendations. Default is 46.

Also note that we are limited by what can be extracted from the
`Clash Royale Developer Api <https://developer.clashroyale.com>`_.

Donations
=========

For each member of the clan, we can see the following:

.. code:: json

    {
        "tag": "#9ULGLRCL",
        "name": "AaronTraas",
        "role": "coLeader",
        "expLevel": 13,
        "trophies": 4688,
        "arena": {
            "id": 54000014,
            "name": "League 3"
        },
        "clanRank": 1,
        "previousClanRank": 1,
        "donations": 505,
        "donationsReceived": 290,
        "clanChestPoints": 72
    }

The only relevant value here is :code:`donations`.

Donations reset on Sunday. And we have as an input constant :code:`TARGET_DONATIONS_PER_DAY`

The algorithm as follows:

1. :code:`days` := the number of days since the reset

2. for each member

   a) :code:`minimumDonations` := :code:`days` * :code:`MINIMUM_DONATIONS_PER_DAY`
   b) :code:`scoreFromDonations` := :code:`minimumDonations` - member's donations
   c) are we at least 1 day after the reset? If yes:

      i. :code:`scoreFromDonations` := :code:`scoreFromDonations` / :code:`days`
      ii. if :code:`days`, :code:`scoreFromDonations` := :code:`scoreFromDonations` + :code:`ZERO_DONATIONS_PENALTY`

Which could leave us with a positive or negative score, based on whether
they meet or fail to meet their target.


War Participation
=================

We get the following per-member war data from the API:

.. code:: json

    {
        "tag": "#9ULGLRCL",
        "name": "AaronTraas",
        "cardsEarned": 800,
        "battlesPlayed": 1,
        "wins": 1,
        "collectionDayBattlesPlayed": 3
    }

Note what this doesn't give us:

* collection battles won (which we can derive through other means)

* war battles assigned (we have no way of getting this for values > 1)

Our scoring takes these limitations into account.

War participation scoring is in turn split into two parts:
`Collection Day Score`_ and `War Day Score`_

Collection Day Score
--------------------

War Day Score
-------------

Total Score
===========

The member's total score is:

	**Donation Score** + **Collection Day Score** + **War Day Score**.

Kick and Demote Recommendations
===============================

If no members are at or below zero, we recommend nothing.

If there are members zero or less, we count how many members over
:code:`CLAN_MINIMUM_MEMBERS`, and recommend kicking that number of
people, chosen from the lowest scores below zero ascending.

If there are more people below zero who have been promoted to *Elder*
or higher, we recommend demoting them.
