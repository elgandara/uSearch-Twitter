import re
import csv
import math
import collections

def erase_link(tweet):
    inx = tweet.find('http')
    #Check to see if tweet contains a link
    if inx != -1:
        #Find white space
        sp_inx = tweet.find(" ", inx)
        #Check if there is a white space after the link
        if sp_inx != -1:
            new_tweet = tweet[0:inx] + tweet[sp_inx + 1:]
        else:
            new_tweet = tweet[0:inx]
        return new_tweet
    return tweet

def normalize(tweet):
    #erase link
    normalizedTweet = erase_link(tweet)
    #print normalizedTweet
    normalizedTweet = re.compile('[^a-zA-Z@]').sub(' ', normalizedTweet)
    normalizedTweet = normalizedTweet.lower()
    normalizedTweet = " ".join(normalizedTweet.split())
    return normalizedTweet
with open("twitter-data/testdata.manual.2009.06.14.csv", 'rb') as csvfile:
    r = csv.reader(csvfile, delimiter=',', quotechar='"')
    docs = [ (x[2], x[4], x[5])  for x in r]
    
tweet_date = [ d[0] for d in docs ] #Tweet dates
tweet_user = [ d[1] for d in docs ] #Tweet users
tweet_text = [ d[2] for d in docs ] #Tweet text

#Normalize each tweet 
tweet_text = map(normalize, tweet_text)

def create_corpus():
    corpus = {}
    for x in range(0,len(tweet_text)):
        corpus[x] = [tweet_date[x], tweet_user[x],tweet_text[x]]
        #print corpus[x]
def create_inverted_index(corpus):
    idx = {}
    
    for i, doc in enumerate(corpus):
        # Iterate through each word in the document
        for word in doc.split():
            if word in idx:
                # Update the document's term frequency
                if i in idx[word]:
                    idx[word][i] += 1
                # Add the document to the word index
                else:
                    idx[word][i] = 1;
            # Add the word to the reversed index
            else:
                idx[word] = {i:1}
    
    return idx
idx = create_inverted_index(tweet_text)

def create_user_index(users):
    
    user_tweets = {}
    
    # Go through each of the tweets in the corpus
    for i in range( len(users) ):
        # When user already exists, add the document id to the existing user tweet list
        if users[i] in user_tweets:
            user_tweets[users[i] ].append(i)
        # Otherwise, creat a new list with the document id
        else:
            user_tweets[users[i] ] = [i]
            
    return user_tweets

user_tweet_index = create_user_index(tweet_user)

def print_results(results, n, head=True):
    ''' Helper function to print results
    '''
    if head:
        print('\nTop %d from recall set of %d items:' % (n, len(results) ) )
        for r in results[:n]:
            print('\t%0.2f | %s | %s' % (r[0], r[2],tweet_text[r[1]]))
    else:
        print('\nTop %d from recall set of %d items:' % (n, len(results) ) )
        for r in results[:n]:
            print('\t%0.2f | %s | %s' % (r[0],r[2], tweet_text[r[1]]))

def idf(term, idx, n):
    return math.log(float(n) / (1 + len(idx[term])))

def get_results_tfidf(qry, idx, n):
    score = collections.Counter()
    for term in qry.split():
        if term in idx:
            i = idf(term, idx, n)
            for doc in idx[term]:
                score[doc] += idx[term][doc] * i
    results=[]
    for x in [[r[0],r[1]] for r in zip(score.keys(), score.values())]:
        if x[1] > 0:
            results.append([x[1],x[0]])
    sorted_results= sorted(results, key=lambda t : t[0] * -1)
    return sorted_results
#results = get_results_tfidf('monkeys', idx, len(tweet_user))
#results = get_results_tfidf('hate', idx, len(tweet_user))
#results = get_results_tfidf('sleep', idx, len(tweet_user))
#results = get_results_tfidf('hate', idx, len(tweet_user))

#print_results(results, 10)


def get_results_bm25(qry, corpus, k1=1.5, b=0.75):
    idx = create_inverted_index(corpus)
    
    # n - the length of the corpus
    n = len(corpus)
    
    # d - list with elements corresponding to the length of each document
    d = [len(x.split()) for x in corpus]
    
    # d_avg - the average document length of the docuemnts in the corpus
    d_avg = float(sum(d) / len(d))
    score = collections.Counter()
    for term in qry.split():
        if term in idx:
            i = idf(term, idx, n)
            for doc in idx[term]:
                # f - the number of times the term appears in the document
                f = float(idx[term][doc])
                # s - the BM25 score for this (term, docuemnt) pair
                s = i * ( (f * (k1 + 1) ) / (f + k1 * (1 - b + (b * (float(d[doc] ) / d_avg) ) ) ) )
                score[doc] += s
                
    results = []
    for x in [ [r[0], r[1], tweet_user[r[0]] ] for r in zip(score.keys(), score.values() )]:
        if x[1] > 0:
            results.append([ x[1], x[0], x[2]])
            
    sorted_results = sorted(results, key=lambda t: t[0] * -1)
    return sorted_results

results = get_results_bm25('hate', tweet_text, k1=1.5, b=0.75)
#print_results(results, 25)


def print_results_username(username_index, user_name):
	if(user_name in username_index):
		# All of the documents that correspond to the username 
		docs = username_index[user_name]
        	# For every doc, print date, username, and tweet 
		for doc in docs:
			print('\t%s | %s | %s' % (tweet_date[doc], tweet_user[doc], tweet_text[doc]))
	else:
        	print "Username does not exist"
    
#results = create_user_index(tweet_user)
#print_results_username(results, 'SimpleManJess')

def determine_query(query):
	#print "(determine_query) " + query 
	if(query[0] == '@' and len(query.split()) == 1):
        	user_choice = raw_input("Select your query preference \n1. All content \n2. User content")
		return user_choice
	return '1'

def u_search(user_choice, query):
    if(user_choice == '1'):
	query = normalize(query)
        results = get_results_bm25(query, tweet_text)
        print_results(results,25)
    if(user_choice == '2'):
	query = query[1:]
        results = create_user_index(tweet_user)
        print_results_username(results, query)
def main():
	query = raw_input("Enter Query: " )
	return query

query = main()
choice = determine_query(query)
u_search(choice,query)

