# A Web Spider

## Where to start

This is based on what we discussed today regarding asynchronous HTTP requests. In the file `homework/solutions/andrew/session1.py` you can find a method called `get_many_using_tasks()`.

## What to do

Either use this function, or write a new one that uses tasks to implement a webspider with the following features.

  - [ ] It should take any number of URLs at it's instantiation.
  - [ ] It should allow a limit to be put on the total number of concurrent downloads.
  - [ ] It should allow a callback to be passed that will operate on those HTTP responses.
  
Save this to a file called `session1-spider.py` and place it in a directory at `homework/solutions/[your name]/`.

Fork this repository, and submit a pull request from your fork to mine.
