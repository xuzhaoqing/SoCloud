# SoCloud
## Introduction
SoCloud is a mini search engine developed by Zhaoqing Xu, and it's the project of CSC326H1: Programming Language in University of Toronto.
## Requirement
python == 2.7

## Lab1 
To check the correctness of lab1, please follow the guidelines:
### Frontend
1. run main.py
"""python
python main.py
"""

2. access localhost:8080 and you will see the interface;

3. input keywords or phrases to check the results and histories

Since I'm still learning CSS, the layout is not very beautiful right now, but it will be improving in lab2.

### Backend
In the `crawler.py` I add two functions: `get_inverted_index()` and `get_resolved_inverted_index()` You could do the following instructions to check it.
1. put the URL you'd like to add in `urls.txt`, by default it only contains `xuzhaoqing.github.io`, which is my personal website.
2. please execute test.py to see the executed result:
"""python
python test.py >log
"""

You could see all the results in log, in which you could see two parts:
```
defaultdict(<type 'set'>, {1: set([1, 2, 3, 4, 5, 6, 7, 11, 12]), 2: set([1, 2, 3, 4, 5, 6, 7, 8, 11, 12]), 3: set([1, 2, 3, 4, 5, 6, 7, 8, 11, 12]), 4: set([1, 2, 3, 4, 5, 6, 7, 8, 11, 12]), 5: set([1, 2, 3, 4, 5, 6, 7, 11, 12]), 6: set([1, 2, 3, 4, 5, 6, 7, 8, 11, 12]), 7: set([1, 2, 3, 4, 5, 6, 7, 11, 12]), 8: set([1, 2, 3, 4, 5, 6, 7, 11, 12]), 9: set([1, 2, 3, 4, 5, 6, 7, 11, 12]), 10: set([1, 2, 3, 4, 5, 6, 7, 11, 12]), 11: set([1, 2, 3, 5]), 12: set([8, 1, 2, 3, 5]), 13
...
```
and 

```
defaultdict(<type 'set'>, {u'1114': set([u'https://xuzhaoqing.github.io/archivers/Prepare-the-Data-2']), u'all': set([u'https://xuzhaoqing.github.io/archivers/Prepare-the-Data', u'https://github.com/xuzhaoqing', 'https://xuzhaoqing.github.io/', u'https://xuzhaoqing.github.io/archivers/Prepare-the-Data-2', u'https://xuzhaoqing.github.io/index', u'https://xuzhaoqing.github.io/about', u'https://xuzhaoqing.github.io/archivers/Write-a-Singularity-Recipe', u'https://xuzhaoqing.github.io/archivers/GSOC-Final-Submission']), u'gt': set([u'https://xuzhaoqing.github.io/archivers/Write-a-Singularity-Recipe']), u'chinese': set(['https://xuzhaoqing.github.io/', u'https://xuzhaoqing.github.io/archivers/Prepare-the-Data-2', u'https://xuzhaoqing.github.io/archivers/GSOC-Final-Submission', u'https://github.com/xuzhaoqing', u'https://xuzhaoqing.github.io/index'])
...
```

which fits the requirements for LAB1, you could dive into crawler.py to see details, and the code is fully commented.

----

## LAB2
### Requirements
1. pip install oauth2client
2. pip install google-api-python-client
3. pip install httplib2
4. pip install beaker
5. pip install boto

