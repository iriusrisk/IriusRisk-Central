## Step-by-step instructions for contributors

As described in the document about [contributing to this project](CONTRIBUTING.md), anyone wanting to add to IriusRisk-Central needs to perform a few steps:

* Create a fork of the [IriusRisk-Central](README.md) library
* Clone that fork to your local machine
* Add your changes to the appropriate directory
* Commit those changes to your fork and push them to GitHub
* Create a pull-request against the IriusRisk-Central repository (**main** branch)

Easy, right? Well, maybe if you're familiar with Git, it is. For everyone else, not so much. 

This document is not a Git tutorial, nor will attempt to teach you anything but the minimum information in order to get you contributing. For anyone wanting to learn more, there are a plethora of tutorials describing all aspects of Git, ad nauseum. 

### The What and Why of Git
Let's start at the begining: Git is a distributed concurrent versioning system that tracks changes to information made by multiple individuals. Important here is *distributed.* Unlike more traditional versioning systems, there is no "source of truth" inherent to Git. Rather, every individual owns there own copy of the project (the so-called "repository"), each just as valid as the next.

That's where GitHub comes in. GitHub performs a few actions:
* It maintains Git repositories
* It handles user management, including authentication and access
* It provides a user interface to view repositories via the web
* It provides a collaboration platform for working on code

The project owners have created a Git repository of the IriusRisk-Central project on GitHub. By convention, we are calling this repository the *most correct* of all potential repositories out there. Therefore, everything starts and ends with it.

### The Repositories
Due to security considerations, you don't get to alter the GitHub repository directly. This is left to the repo owners and managers. You can, however, ask that *they* alter it for you. This is the so-called *pull-request*. You make a pull-request, and the owners of the repo decide if they want to accept it or not.

So-described, it should be clear why you need to request someone *pull* something, rather than *push*, or *commit*, or whatever. You have the changes you want to make part of the repo, and don't have the rights to push them. So someone else has to pull them in. You just need to ask.

This also explains why we talk about multiple *repositories* rather than just one. Ultimately, *three* repositories are going to be used by following the instructions below:
1. The IriusRisk repo on GitHub
2. A clone of that repo, owned by you, also on GitHub
3. *Another* clone of that repo on your local machine.

The actual actions are less complex that this might make it seem. It is nonetheless helpful to remember this structure in order to understand what's going on.

### Pre-requisites

A few things are required for the step-by-step instructions:
* A GitHub account ([Signing up to GitHub](https://docs.github.com/en/get-started/signing-up-for-github/signing-up-for-a-new-github-account))
* A computer with Git command-line (Git BASH) installed ([Installing Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git))
* Successful authentication between the two ([Authentication to GitHub](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/about-authentication-to-github))

There are other ways to contribute, for instance directly via the GitHub UI, or using a thick client on a computer. The steps below, however, are fairly straight-forward and should aid you in any case.

### Step 1: Forking the Repo

The first step is to make the IriusRisk-Central repo your own. By this I mean creating a fork of the repository and storing it in GitHub. (Don't worry! This won't have any effect on the original repo.) This is easy to do:
* Navigate to the [IriusRisk-Central repo homepage](https://github.com/iriusrisk/IriusRisk-Central)
* Click the drop-down next to *fork*
* Click *create a new fork*

![Repo fork drop-down](/~assets/create-fork.png)

* Click *Create fork* after adjusting the options (typically the default options are fine)

![Repo fork options and approval](/~assets/create-fork-2.png)

Once the forked repo is created, you will be taken to its new homepage.

### Step 2: Cloning the New Repo

Next, you need to make a copy of the new repo (*clone* it) on your local computer. 
* Click the green *Code* button on the fork landing page
* Make sure the SSH tab is selected
* Click the *copy* icon to the right of the repo path

![Get the clone URL](/~assets/clone-repo.png)

* Open the Git BASH interface
* Navigate to the directory where you want to store the code
* Type in "git clone \<URL\>" (where **\<URL\>** is the URL copied above) and click return

![Clone the repo locally](/~assets/git-clone-1.png)

You should now have a new local directory which contains the entire contents of the IriusRisk-Central repo.

### Step 3: Do Your Voodoo
At this point, the most recent code from the library is on your file system. You can do with it what you want--edit it, add to it, remove things. How you do this is up to you. Use your favorite editor, for instance, or simply drag-and-drop items to the sub-directories.

Once you've made the changes you wanted, it's time to move things back to GitHub.

### Step 4: Commit and Push Your Changes
Remember that there are *three* repositories we are working on. Git notices when you add and edit files, but won't do anything about it at first. You have to tell it what to do. For instance, for this example I added a template to the Templates directory, and edited its README.md file. 

![Unstaged changes to git](/~assets/git-unstaged.png)

To add those changes, do the following:
* Open Git BASH, and navigate to the base of the repo
* Type *git add \<files\>* (where \<files\> are one or more paths to altered or added files)
* Type *git commit -m 'descriptive commit note'* (the note should be a short description of what it is you're adding)
* Type *git push*

Here you've done several things:
* You told Git exactly which files you wanted to work with
* You added those files (*committed*) to your local repository, and
* You uploaded (*pushed*) those files to your repository on GitHub

Your changes are now stored on the GitHub repository. You can now ask those changes to be added to the main IriusRisk-Central repository!

### Step 5: Make a Pull Request
This is often the simplest part of the process. You need to inform the managers of the repository that you've made changes, and ask them to bring them into the repository for everyone else. You can do this directly from your forked repository on GitHub.

* Navigate to the homepage of your IriusRisk-Central fork on GitHub
* Click the drop-down next to *Contribute* 
* Click the green *Open pull request* button

![Showing fork is ahead of main](/~assets/branch-is-ahead.png)

As soon as you navigate to your GitHub fork, you will be told that you have changes the original repo doesn't have. The request form appears once you clicked *create.* Add the necessary information, especially a description of what you are adding, and click the green *Create pull request.*
![Pull request form](/~assets/open-pull-request.png)

You're done! You now see a page describing the pull request, including the status it's in. The manages of IriusRisk-Central are informed automatically of the request and will begin processing it. You will see the workflow steps, including once they've accepted it, right here at the pull request home page.

![Pull request status page](/~assets/pull-request-opened.png)