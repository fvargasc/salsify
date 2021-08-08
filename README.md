# Software Requirements
The present deliverable has been set up to use Docker and docker-compose.
The motivation for this choice was to ensure easy configuration and execution across multiple platforms and running environments.

The functions for these tools are as follows:

- Docker : Configure, build and launch the application containers.
- Docker-compose : Orchestrate container execution and set volume and environment configurations.

Note:
For best performance, docker should be executed natively on a Linux machine.


# How to Execute

System execution requires the following steps:

1. Set current working directory to the <b>root</b> of the repository.
2. Launch the <b>build.sh</b> script.
3. Place the target text file in the <b>input_files</b> directory (required due to volume management).
4. Launch the <b>run.sh</b> script, adding the <b>name</b> of the input file to use as the first argument. 
   
    Example:
   
        $ sh run.sh sample.txt

      Once the system has finished launching, the endpoint will be available on:
        
        http://localhost:5000/lines/<line_number>

Notes:
Generated index files will be kept throughout different executions. In order to regenerate the index for a file, 
one must delete the existing index before executing.

Example:

    input_files -|
                 |- sample.txt
                 |- sample.txt.idx   <--- delete this

# System Overview
The current repository contains the configuration and source-code for a system that complies with the requirements stated [here](./docs/Line Server Problem.pdf).

The system is composed of 2 modules:

- App : The web application reachable through the requested endpoint (GET /lines/<line_number>).
- Line Index : Text file pre-processing and index generation. Implements the inspection of the provided text file, and 
  the generation of a second file containing the index of each line of text.

### Execution flow
1. The system begins by reading the text file provided as an argument, by opening a read stream to it.


2. As the text file (e.g. sample.txt) is being parsed for its lines, a corresponding index file is being written (e.g. sample.txt.idx)
under the same directory. 

The content of the index file is a sequence of fixed 64-bit integer values. Each entry in the <b>index file</b> contains
the offset (in bytes) of the first character for a corresponding line in the <b>text file</b>. 

Example:

<u>sample.txt</u>

    I am a line and I begin at position 0
    I'm another one starting in position 38
    I'm 78 characters in
    I'm the last one and I have an offset of 99 bytes

<u>sample.txt.idx</u> (shown in base 10)

    000...0 000...38 000...78 000...99

3. Once the index file has been built, the web application is launched and made available on TCP <b>port 5000</b> (e.g. http://localhost:5000).


4. When a GET request is dispatched to the <i>lines</i> endpoint with the requested line's number as an url path parameter.
   The application performs a lookup on the index file at the corresponding segment, and reads the offset value for the requested line.
   Lastly, the offset value is used to look up the source text file at that offset, and responds with the line that follows it (terminated with \n).
   
    <b>Mind that the line numbers are zero based.</b> i.e. the number of the first line is 0.
   

# Core Technologies
The system is built using the [Python (v3) language](https://www.python.org).
This language was chosen for its simplicity of use and readability, as well as its robustness and maturity.

Python is an interpreted language and is slightly less performant than existing alternatives (e.g. Ruby).
However, as this is a simple system, these small differences should not be noticeable.


# Application dependencies

### Flask
The application is developed using the lightweight Web framework [Flask](https://flask.palletsprojects.com).

This framework is broadly adopted for its simplicity and lightweight. It provides the system developer with the necessary 
tools in order to build complex user-facing web applications, but also simple route-based APIs, as is the case with 
this system.

This framework was chosen for its simplicity, robustness, performance and ease of use, which cater to the requirements 
of the challenge.

Applications written using Flask are also standards-compatible with WSGI Web Servers.


### gunicorn
The system uses the [gunicorn Web Server](https://gunicorn.org) in order to deliver the application endpoint through HTTP.

It is a simple and light Web Server that is WSGI compliant.

Gunicorn was chosen for being light on resources, simple in its implementation and configuration, and also for its robustness.


# Performance
The system's performance is bounded by the following constraints:
- Processing capability: The number of available processor cores and respective processing capability set a limit for 
  processing speed of isolated requests.


- Available memory: Even though memory usage <b>does not scale with input</b>, the web server uses a limited number of App processes to 
increase response capability and speed. There should be enough memory available for each process. 


- Available persistent storage: Disk storage should be enough to contain the original text file, as well as the 
  generated index files. Each index file has a size of <b>8 * number_of_text_lines</b> bytes.


- Persistent storage throughput: As storage I/O is highly intensive for this system, the throughput capabilities may impact
the overall response speed.


- Network throughput: The network's capability to carry the required network traffic may have significant influence in 
the system's ability to support timely concurrent requests, through excessive resource occupation. 


- Operating system: Operating systems may impose limits on the number of open connections and general file descriptors.


- Parallelization: The App's design allows for process replication (same or multiple machines), although this 
  deliverable does not include an example or configurations for that setup.
  
    The index generation process is not set up to be parallelized. Useful parallelization could however be achieved for 
this process, given that the file were itself fully or partially replicated (e.g. sharding) in order to spread the 
  load for storage I/O.

  
# Questions and answers

- <b>Q</b>. How does your system work?
    
    <b>A</b>. Refer to [System Overview](#system-overview).


- <b>Q</b>.How will your system perform with a 1 GB file? a 10 GB file? a 100 GB file? 
  
    <b>A</b>.  Apart from the bounds listed in [Performance](#performance), the <b>indexing algorithm presents linear 
  complexity</b> with relation to the size and number of lines in the source text file. 
  
    To provide an example, the system was tested with a <b>1GB file, taking circa 7s</b> to index.

    Under the same runtime conditions, the time is expected to increase to <b>70s for a 10GB</b> file, and 
  <b>700s (<12min) for a 100.000GB</b> file.
  
  
- <b>Q</b>.How will your system perform with 100 users? 10000 users? 1000000 users?

    <b>A</b>.  The <b>line retrieval algorithm</b> has <b>constant complexity</b>, as the line may be obtained from a direct 
  file lookup, using the line number as the argument.
  
    As such, given enough parallel processes, within the bounds listed in [Performance](#Performance), the system should 
  perform, regardless of the number of users.
  
    The system was load tested with up to 1000 simultaneous connections (load test users), looping continuously and 
  without delay between each request.
  
    On an 8-year-old Macintosh laptop the system handled a throughput of over 1300 requests per second continuously, 
  through the loopback device (localhost).
  
    Under these runtime conditions, the system responded successfully to:
    - 100 requests in 1.33s
    - 1.000 requests in 4s
    - 10.000 requests in 10s
    - 100.000 requests in 93s
    - 1.000.000 requests in 873s (14.33min) 
    
  
- <b>Q</b>. What documentation, websites, papers, etc did you consult in doing this assignment?
  
  <b>A</b>. I checked the documentation pages for python3, Flask, gunicorn and docker-compose. 
  Used google and stack overflow as aides to overcome a few small hurdles. 
  Also checked out the source code for the 'wc' (wordcount) command, which solves similar file-related problems.


- <b>Q</b>. What third-party libraries or other tools does the system use? How did you choose each library or 
  framework you used?
  
  <b>A</b>. Technologies were chosen generally for their simplicity of use, readability, maturity and adoption 
  in the developer community. 
  For more details, refer to the [Application dependencies](#Application dependencies) section.


- <b>Q</b>. How long did you spend on this exercise? 
  If you had unlimited more time to spend on this, how would you spend it and how would you prioritize each item?
  
  <b>A</b>. Design and Development were spread throughout circa 4 hours, with actual work taking a ballpark of 2.5hours.
  
  Load testing and tuning took another hour, and documentation is taking 1.5 hours.

  Assuming <b>performance and reliability</b> to be THE goals, further developments would be (in order of priority):
      
      1. Automate functional and load testing
      2. Provide cache-related headers in the http response (etag, cache-control)
      3. Add a reverse proxy in order to offload partial connection management and response caching (nginx)
      4. Automate deployment
      5. Parallelize the index generation process
      6. Add support for distributed deployment of the web app (e.g. kubernetes, serverless)
      7. Set up system metrics and alarms
      8. Add better logging
      9. Add support for analytics
      10. Add load balancing to the web app (depends on 6)
      11. Add auto-scaling to web app (depends on 6)
      12. Prototype system using highly performant technologies (e.g. go, rust, c++)

  Items were prioritized according to the perceived amount of value delivered in the shortest possible time.


- <b>Q</b>. If you were to critique your code, what would you have to say about it?
  
  <b>A</b>. The code was kept very simple, using symbol names that are hopefully easy to understand.
  The fact that this is a very simple and concise system, leads me to lean towards promoting readability
  rather than structure.
  
  A larger and more complex system would require the program components to follow a more systematised structure, and the
  organisation of the program's files would need to follow that.
  
  In this case, I opted to include an extra amount of comments, to make sure my intents are clear, but these have the
  effect of making the source code dirtier and more dense.
  
  I try to avoid 'clever' code which usually compromises readability. 
  Ideally (and hopefully), the code should be self-explanatory.

