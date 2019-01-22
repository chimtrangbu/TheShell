# The Shell
My biggest project so far.

# Core project
## Introduction
Last week you discovered what exactly was the shell, that useful tool that allows you to execute commands transparently in a terminal window.

So, now you know the basic mechanism for reading commands and executing them in a different process - it's a good start! But the shell is more complex than that. First, it's a programming language in itself, with variables, loops & conditionals. It also allows you to control precisely the execution of programs, as you can interrupt them & start them up again. All of this is done in a user-friendly manner thanks to some things like command-line edition and access to the command history...

The main difficulty of the shell project isn't so much the different functionalities (though some of the bonuses are actually really difficult to pull off in a short time), but the organisation of your team. You need to plan carefully what features you want to implement & design your program accordingly, and you need to test everything extensively.

## Your mission
You will continue the work you started last week with the minish. Your mission over the next 3 weeks is to implement additional functionalities to make your shell as usable as possible... but be careful to keep your program stable at all times!

I cannot stress this enough: your shell must be perfectly stable and never crash! Don't bother adding new functionalities if your base is not solid, you won't get any points.

There are also two main organisational constraints for this project:

- You will have to respect a proper Gitflow (see below)
- You won't have any Sentinel credits. It's up to you to develop enough tests (either automated test scripts or test cases that you run by hand) to ensure your shell is stable.

Your program will be called `intek-sh.py` and be present at the root of your git repository. You are free to organise your repository however you like and have as many files as necessary.

## Gitflow
The rules are simple enough. You will have three types of branches:

- The master branch is for the "releases". You will have to do one release for the peer review, and one final for the staff review. The releases must absolutely be stable!
- A develop branch for integrating all features and preparing the releases.
- As many feature branches as necessary. Each feature must have its own branch. Each feature branch will have to be tested extensively and be stable before being merged into the develop branch.

All branches will be checked during the review to ensure you followed the process, so don't delete your features branches after merging them into the develop branch.

Each feature branch must have a self-descriptive name.

For more information on Gitflow, you might refer to this:

https://datasift.github.io/gitflow/IntroducingGitFlow.html

## The features
First, that's a given, your shell has to respect all the rules of the minish. That's kind of the starting point.

Now, here is the list of features you may add, with an estimation of their difficulty:

    globbing ★✩✩✩
    path expansions (tilde expansions, parameter expansions) ★✩✩✩
    pipes & the redirections >, <, >> and << ★★★✩
    handling the exit status of commands ★✩✩✩
    command substitution with the backquotes ★★✩✩
    logical operators && and || ★★✩✩
    signals handling ★★✩✩
    subshells with () ★★✩✩
    quoting (quotes & escape characters) ★✩✩✩
    command-line edition with the curses module (being able to move the cursor with arrows left & right to edit some part of the line, key combination of your choice to go at the beginning & at the end of the line, arrows up & down to move inside the history...) ★★★✩
    the command history with the builtins history and ! ★★✩✩
    dynamic command completion ★★✩✩
You have to pick at least 6 of those features and implement them. The more the better... as long as everything's stable!

## The Bible
bash will be your shell of reference. If you don't know how something works, the outputs, the error messages... test it on bash!

Here's an exhaustive reference describing the POSIX standard for the shell language: http://pubs.opengroup.org/onlinepubs/009695399/utilities/xcu_chap02.html

Don't worry if most of it flies over your head, you don't have to read it all, you can just use it to understand the features you want to implement.

And don't forget to exchange a lot with your fellow students! There are features you won't implement that you can still discover through other students. Also, don't hesitate to ask if you have any questions.
  
# BONUSES
## Should you do bonuses?
The following bonuses are difficult to implement, either because there are many special cases (job control, I'm looking at you) or because they have an heavy influence on the design of the project, with no guarantee that you'll finish them on time (that's for the shell script).

But they are also extremely gratifying. Implementing the shell script is very rewarding as you touch at the essence of programming languages, and job control is quite satisfying as you get to really understand how the system orchestrates processes.

I encourage you to consider those bonuses if you want a good challenge, though you need to be very careful in the way you design your program. You don't want to end up with an unstable shell because those features are half-finished!

## Job control ★★★★
Implement job control with the operator & and the builtins jobs, fg, bg.

Job control implies some special handling for compound commands (pipes, subshells...) & affects signals handling as well, so you need to have those implemented and stable first. There's not a lot of code to produce, but a really good understanding of system internals is required.

## Shell script ★★★★
To implement shell script, you need to handle the POSIX shell grammar. You'll need to research how to generate an abstract syntax tree (lexing and parsing will give you one!), and you will need to code the execution of that AST.

The raw difficulty probably lies around the concept of lexing and parsing. You can use tools like Lex & Yacc to abstract that difficulty if you are short on time, though building your own lexer & parser would be pretty cool.

The second difficulty is that it's harder to test the execution without having the AST, so it might be difficult to build the AST and code its execution in parallel.
