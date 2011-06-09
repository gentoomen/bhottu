from api import *
import time

# TODO: poll timer support

def load():
    """Implements a poll system."""
    dbExecute('''create table if not exists polls (
              pollID int auto_increment primary key,
              question text,
              active bool )''')
    dbExecute('''create table if not exists answers (
              answerID int auto_increment primary key,
              pollID int,
              `index` int,
              answer text,
              unique(pollID, `index`) )''')
    dbExecute('''create table if not exists votes (
              voteID int auto_increment primary key,
              answerID int,
              nick varchar(255),
              index(answerID, nick) )''')
    registerFunction("open poll %S", openPoll, "open poll <question>", restricted = True)
    registerFunction("close poll", closePoll, restricted = True)
    registerFunction("show poll %!i", showPoll, "show poll [poll ID]")
    registerFunction("vote for %i", voteFor, "vote for <answer ID>")
    registerFunction("vote new %S", voteNew, "vote new <answer>")
    registerFunction("search poll %S", searchPoll, "search poll <search term>")
    registerFunction("delete poll %i", deletePoll, "delete poll <poll ID>", restricted = True)
registerModule("Poll", load)

def openPoll(channel, sender, question):
    """Creates a new poll."""
    if len(dbQuery("SELECT pollID FROM polls WHERE active = 1")) > 0:
        sendMessage(channel, "There already is an open poll.")
        return
    dbExecute("INSERT INTO polls (question, active) VALUES (%s, 1)", (question, ))
    log.info("Opened new poll: %s" % question)
    sendMessage(channel, "Poll opened!")

def closePoll(channel, sender):
    """Closes the current poll."""
    if len(dbQuery("SELECT pollID FROM polls WHERE active = 1")) == 0:
        sendMessage(channel, "No poll is open at the moment.")
        return
    sendMessage(channel, "Pool's closed.")
    for (answer, votes) in dbQuery("SELECT answer, count(voteID) FROM polls INNER JOIN answers ON answers.pollID = polls.pollID LEFT JOIN votes ON votes.answerID = answers.answerID WHERE active = 1 GROUP BY answers.answerID, answer ORDER BY count(voteID) DESC LIMIT 1"):
        sendMessage(channel, "Winning entry: '%s' with %s votes" % (answer, votes))
    dbExecute("UPDATE polls SET active = 0")

def showPoll(channel, sender, pollID):
    """Shows the answers for a given poll."""
    if pollID == None:
        poll = dbQuery("SELECT pollID, question FROM polls WHERE active = 1")
        if len(poll) == 0:
            sendMessage(channel, "There's no poll open.")
            return
    else:
        poll = dbQuery("SELECT pollID, question FROM polls WHERE pollID = %s", pollID)
        if len(poll) == 0:
            sendMessage(channel, "No such poll found.")
            return
    pollID = poll[0][0]
    question = poll[0][1]
    sendMessage(channel, question)
    for (index, answer, votes) in dbQuery("SELECT `index`, answer, count(voteID) FROM answers LEFT JOIN votes ON votes.answerID = answers.answerID WHERE pollID = %s GROUP BY answers.answerID, `index`, answer ORDER BY `index` ASC", (pollID, )):
        sendMessage(channel, "%s. %s (%s)" % (index, answer, votes))

def voteFor(channel, sender, answerIndex):
    """Casts a vote for the current poll."""
    polls = dbQuery("SELECT pollID FROM polls WHERE active = 1")
    if len(polls) == 0:
        sendMessage(channel, "No poll is open at the moment.")
        return
    pollID = polls[0][0]
    answers = dbQuery("SELECT answerID FROM answers WHERE pollID = %s AND `index` = %s" % (pollID, answerIndex))
    if len(answers) == 0:
        sendMessage(channel, "No item #%s found." % answerIndex)
        return
    answerID = answers[0][0]
    dbExecute("DELETE FROM votes WHERE nick = %s AND answerID IN (SELECT answerID FROM answers WHERE pollID = %s)", (sender, pollID))
    dbExecute("INSERT INTO votes (answerID, nick) VALUES (%s, %s)", (answerID, sender))
    sendMessage(channel, "Vote registered.")

def voteNew(channel, sender, answer):
    """Creates a new possible answer for the current poll and votes for it."""
    polls = dbQuery("SELECT pollID FROM polls WHERE active = 1")
    if len(polls) == 0:
        sendMessage(channel, "No poll is open at the moment.")
        return
    pollID = polls[0][0]
    maxIndex = dbQuery("SELECT MAX(`index`) FROM answers WHERE answers.pollID = %s", pollID)[0][0]
    if maxIndex == None:
        index = 1
    else:
        index = maxIndex + 1
    dbExecute("INSERT INTO answers (pollID, `index`, answer) VALUES (%s, %s, %s)", (pollID, index, answer))
    answerID = dbQuery("SELECT answerID FROM answers WHERE pollID = %s AND `index` = %s", (pollID, index))[0][0]
    dbExecute("DELETE FROM votes WHERE nick = %s AND answerID IN (SELECT answerID FROM answers WHERE pollID = %s)", (sender, pollID))
    dbExecute("INSERT INTO votes (answerID, nick) VALUES (%s, %s)", (answerID, sender))
    sendMessage(channel, "Vote added.")

def searchPoll(channel, sender, searchTerm):
    """Search polls matching a given search term."""
    polls = dbQuery("SELECT pollID, question FROM polls WHERE question LIKE %s", ('%' + searchTerm + '%',))
    if len(polls) == 0:
        sendMessage(channel, "No polls found.")
        return
    if len(polls) > 3:
        sendMessage(channel, "%s entries found, refine your search" % len(polls))
        return
    for (pollID, question) in polls:
        winners = dbQuery("SELECT answer, count(voteID) FROM answers INNER JOIN votes ON votes.answerID = answers.answerID WHERE pollID = %s GROUP BY answers.answerID, answer ORDER BY count(voteID) DESC LIMIT 1", (pollID, ))
        if len(winners) == 0:
            sendMessage(channel, "%s. %s" % (pollID, question))
        else:
            sendMessage(channel, "%s. %s -- Winner: %s (%s)" % (pollID, question, winners[0][0], winners[0][1]))

def deletePoll(channel, sender, pollID):
    """Deletes a poll from the archives."""
    if len(dbQuery("SELECT pollID FROM polls WHERE pollID = %s", (pollID, ))) == 0:
        sendMessage(channel, "No such poll found")
    dbExecute("DELETE FROM votes WHERE answerID IN (SELECT answerID FROM answers WHERE pollID = %s)", (pollID, ))
    dbExecute("DELETE FROM answers WHERE pollID = %s", (pollID, ))
    dbExecute("DELETE FROM polls WHERE pollID = %s", (pollID, ))
    sendMessage(channel, "Poll deleted.")
