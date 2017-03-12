#!/usr/bin/env python2

import sys
import re
import mmh3
from docreader import DocumentStreamReader


class MinshinglesCounter:
    SPLIT_RGX = re.compile(r'\w+', re.U)

    def __init__(self, window=5, n=20):
        self.window = window
        self.n = n

    def count(self, text):
        words = MinshinglesCounter._extract_words(text)
        shs = self._count_shingles(words)
        mshs = self._select_minshingles(shs)

        if len(mshs) == self.n:
            return mshs

        if len(shs) >= self.n:
            return sorted(shs)[0:self.n]

        return None

    def _select_minshingles(self, shs):
        buckets = [None]*self.n
        for x in shs:
            bkt = x % self.n
            buckets[bkt] = x if buckets[bkt] is None else min(buckets[bkt], x)

        return filter(lambda a: a is not None, buckets)

    def _count_shingles(self, words):
        shingles = []
        for i in xrange(len(words) - self.window):
            h = mmh3.hash(' '.join(words[i:i+self.window]).encode('utf-8'))
            shingles.append(h)
        return sorted(shingles)

    @staticmethod
    def _extract_words(text):
        words = re.findall(MinshinglesCounter.SPLIT_RGX, text)
        return words


def main():
    mhc = MinshinglesCounter()

    res = {}
    doc_names = {}
    counter = 0
    for path in sys.argv[1:]:
        for doc in DocumentStreamReader(path):

            counter += 1
            doc_names[counter] = doc.url
            minsh = mhc.count(doc.text)

            if minsh is None:
                continue

            for sh in minsh:
                tmp = res.pop(sh, [])
                tmp.append(counter)
                res[sh] = tmp

    count_pairs = {}
    for l in res:
        curr = res[l]
        for i in range(0, len(curr)):
            for j in range(i + 1, len(curr)):

                tmp = (curr[i], curr[j])

                if curr[i] > curr[j]:
                    tmp = (curr[j], curr[i])

                count_pairs[tmp] = count_pairs.pop(tmp, 0) + 1

    for (a, b) in count_pairs:

        m = count_pairs.get((a, b))
        if m is None or a == b or doc_names.get(a) == doc_names.get(b):
            continue
        l = (1.0 * m) / (mhc.n + mhc.n - m)
        if l > 0.75:
            print doc_names.get(a) + " " + doc_names.get(b) + " " + str(l)

if __name__ == '__main__':
    main()
