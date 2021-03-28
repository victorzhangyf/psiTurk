```eval_rst
.. toctree::
   :caption: First Steps
   :maxdepth: 2
   :hidden:

   forward
   quickstart
   anatomy_of_project
   command_line_overview
   dashboard
   recording
   retrieving

.. toctree::
  :caption: Topic Guides
  :maxdepth: 2
  :hidden:

  install
  amt_setup
  tutorials/heroku
  customizing
  topic_guides/alternative_channels

.. toctree::
  :caption: Tutorials
  :maxdepth: 2
  :hidden:

  tutorials/example-project-stroop
  tutorials/using_jspsych
  tutorials/static_ip_ssl
  tutorials/external_surveys
  tutorials/cookbook

.. toctree::
  :caption: Reference Guides
  :maxdepth: 2
  :hidden:

  api
  settings
  command_line
  migrating

.. toctree::
  :caption: Support
  :maxdepth: 2
  :hidden:

  disclaimer
  getting_help
  Discussion forum <https://discuss.streamlit.io/>
  roadmap
  contribute
  Source code & issue tracker <https://github.com/nyuccl/psiturk/>
```

# Welcome to psiturk

[**psiturk**](https://psiturk.org/) is an open-source Python library that makes it easy to create high-quality behavioral experiments that are delivered over the Internet using a web browser.  

psiturk is not, _by itself_, used for creating surveys or interfaces in the browser (for that we recommend tools like [jspych](https://www.jspsych.org) or [d3.js](https://d3js.org)).  Instead, psiturk solves all the _other_ myriad of problems that come up in web experimentation including:
- reliably and securely serving webpages to participants over the internet
- blocking repeat participation (when desired)
- counterbalancing conditions
- incrementally saving data to databases
- simplifying the process of soliciting and approving work on crowdworking sites

In addition to making it easy to run simple, standard experiments it enables much more complex designs including adaptive tasks where for instance a computational model might run on the server (in e.g., Python) and process the participants' data in real time to change the stimuli presented later in a task.

psiturk provides a flexible but standardized workflow for online experiment development.  We do all this in an open and free development environment that draws from the community to share best practices.  We don't want your money but we accept bug reports, feature requests, and -- even better -- pull requests**🎈**!

## Video introduction

Still unsure if psiturk is for you?  Try this quick five minute video introduction!

---

## How to use our docs

The docs are broken up into several sections:

- **First Steps**: include our [Key Concepts](key_concepts.md) and [Get Started](getting_started.md) guide give a general overview to getting started with **psiturk**.

- **Topic guides**: give you background on specific aspects of **psiturk**. Make sure to check out the sections on [Example project walk-through](main_concepts.md) and [Deploying an app](deploy_streamlit_app.md), and [Customizing psiturk](develop_streamlit_components.md).

- **Tutorials**: provides high level overview of common project cases.  Make sure to check out the sections on the sample project walk-through and using jsPsych+psiturk.

- **Cookbook**: provides short code snippets and tips that might find useful.

- **Reference guides**: are the bread and butter of how our [APIs](api.md) and [configuration files](streamlit_configuration.md) work and will give you short, actionable explanations of specific functions and features.

- **Support**: gives you more options for when you're stuck or want to talk about an idea. Check out our discussion forum as well as a number of [troubleshooting guides](/troubleshooting/index.md).

---

## Open source, community-built, widely used

psiturk accomplishes these goals within a community-oriented development approach. The software is released under the [MIT License](https://github.com/NYUCCL/psiTurk/blob/master/LICENSE). Version 1.0 was launched in November 2013 and since then **psiturk** has maintained a diverse, supportive, and engaged open-source development community that includes over 40 contributors on github and over 1800 commits.  We have an active and supportive mailing list and try to promptly give feedback and incorporate pull requests from contributors from all over the world with many different skill levels.

**psiturk** is used in research from cognitive science, psychology, neuroscience, bioinformatics, marketing, computer security, user interface testing, computer science, machine learning in both academic and industry.  We don't want to brag but it is used at some fancy places.  

Odds are pretty good that if you are thinking "should I start from scratch with Flask or node.js to implement my Mechanical Turk experiment" the answer is no, use **psiturk** and save yourself a lot of time.



## **Join the community**

Please come join us on the [community forum](https://groups.google.com/forum/#!forum/psiturk) or follow us on [twitter](https://twitter.com/psiturk).  We love to hear your questions, ideas, and help you work through your bugs on our github [issues tracker](https://github.com/NYUCCL/psiturk/issues)!  The project leaders are [Dave Eargle](https://daveeargle.com) and [Todd Gureckis](http://gureckislab.org).


   ```eval_rst
   .. note::

      **Citing this project in your papers**:

      To credit **psiturk** in your work, please cite both the original journal paper and a version of the Zenodo archive.  The former provides a high level description of the package, and the latter points to a permanent record of all psiturk versions (we encourage you to cite the specific version you used). Example citations (for psiTurk 3.0.6):

      **Zenodo Archive**:  

      Eargle, David, Gureckis, Todd, Rich, Alexander S., McDonnell, John, & Martin, Jay B. (2021, March 28). 
      psiTurk: An open platform for science on Amazon Mechanical Turk (Version v3.0.6). Zenodo. http://doi.org/10.5281/zenodo.3598652

      **Journal Paper**:  

      Gureckis, T.M., Martin, J., McDonnell, J., Rich, A.S., Markant, D., Coenen, A., Halpern, D., Hamrick, J.B., Chan, P. (2016) psiTurk: An open-source framework for conducting replicable behavioral experiments online. Behavioral Research Methods, 48 (3), 829-842.	DOI: http://doi.org/10.3758/s13428-015-0642-8 
   ```