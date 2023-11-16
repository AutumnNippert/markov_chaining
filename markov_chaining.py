import random
import pickle
import sys
import re

class MarkovChain:
    def __init__(self, printing=False):
        self.map = {} # {obj : [{next_obj : count}, {next_obj : count}, ...]}
        self.objects = [] # [obj, obj, obj, ...]
        self.printing = printing

    def __str__(self):
        retstr = ''
        for obj in self.map.keys():
            retstr +=f'{obj} : {self.map[obj]}\n'
        return retstr
    
    def __repr__(self):
        return str(self)
    
    def importFile(self, file_name, regex=r'[\w\']+'):
        if self.printing:
            print(f"Importing {file_name}...")
        with open(file_name, 'r', encoding='utf-8') as f:
            contents = f.read()
            self.objects = re.findall(regex, contents)
        if self.printing:
            print(f"Imported {file_name}.")

    def importObjectList(self, objects):
        if self.printing:
            print(f"Importing {len(objects)} objects...")
        self.objects = objects
        if self.printing:
            print(f"Imported {len(objects)} objects.")

    def importObjectLists(self, objects):
        if self.printing:
            print(f"Importing {len(objects)} object lists...")
        for obj_list in objects:
            self.objects += obj_list
        if self.printing:
            print(f"Imported {len(objects)} object lists.")

    def appendObject(self, obj):
        self.objects.append(obj)
    
    def printProgress(current, total, printInterval=100):
        if current % printInterval == 0 or current == total:
            percent_complete = current / total * 100
            pc_str = '=' * int(percent_complete / 2)

            sys.stdout.flush()
            sys.stdout.write(f"\rTraining | {pc_str.ljust(50, ' ')} | Line {current} / {total}")

    def train(self):
        # get all words in "words", and get the next word after it, and add that to the dictionary so the dictionary looks like this: {word : [{next_word : count}, {next_word : count}, ...]}
        for i in range(len(self.objects) - 1):
            if self.printing:
                MarkovChain.printProgress(i, len(self.objects))
            
            if self.objects[i] not in self.map:
                self.map[self.objects[i]] = [{self.objects[i+1] : 1}]
            else:
                found = False
                for nextObj in range(len(self.map[self.objects[i]])):
                    if self.objects[i+1] in self.map[self.objects[i]][nextObj]:
                        self.map[self.objects[i]][nextObj][self.objects[i+1]] += 1
                        found = True
                        break
                if not found:
                    self.map[self.objects[i]].append({self.objects[i+1] : 1})
                    
        if self.printing:
            MarkovChain.printProgress(len(self.objects), len(self.objects))
            print()
    
    def savePolicy(self, file, readable=False):
        fw = open(file, 'wb')
        pickle.dump(self.map, fw)
        fw.close()

        if not readable:
            return

        # write it to a file new line separated
        with open(f'readable_{file}', 'w', encoding='utf-8') as f:
            for obj in self.map.keys():
                f.write(f'{obj} : ')
                for nextObj in range(len(self.map[obj])):
                    for occurrences in self.map[obj][nextObj]:
                        f.write(f'{occurrences} ({self.map[obj][nextObj][occurrences]}) ')
                f.write('\n')


    def loadPolicy(self, file):
        fr = open(file, 'rb')
        self.map = pickle.load(fr)
        fr.close()
                        
    def getNext(self, obj):
        if obj not in self.map:
            return None
        else:
            total = 0
            for nextObj in range(len(self.map[obj])):
                for occurrences in self.map[obj][nextObj]:
                    total += self.map[obj][nextObj][occurrences]
            rand = random.randint(1, total)
            for nextObj in range(len(self.map[obj])):
                for occurrences in self.map[obj][nextObj]:
                    rand -= self.map[obj][nextObj][occurrences]
                    if rand <= 0:
                        return occurrences
            return None
        
def getStartingWord(markov_chain):
    # for word in markov_chain.map.keys():
    #     if word[0].isupper():
    #         return word
    # return None
    # Get Random Uppercase Word from the list of objects
    while True:
        word = random.choice(markov_chain.objects)
        if word[0].isupper():
            return word
    return None
            
def generateSentence(markov_chain, startingWord, length):
    sentence = startingWord
    for i in range(length):
        nextWord = markov_chain.getNext(startingWord)
        if nextWord == None:
            break
        sentence += ' ' + nextWord
        startingWord = nextWord
    return sentence

def converse(markov_chain):
    print('Lets have a conversation :3')
    print('_________________________________')
    while True:
        message = input('>> ')
        if message == 'exit':
            break
        #mc.addContext(message)
        print()
        print(generateSentence(markov_chain, getStartingWord(markov_chain), 50))
        print('_________________________________')
    
def main():
    mc = MarkovChain(printing=True)
    mc.importFile('transcript.txt')
    mc.train()
    mc.savePolicy('policy.pkl', True)
    converse(mc)
    return
    
if __name__ == "__main__":
    main()