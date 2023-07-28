
# git-collaborative-workflow
## The most common usage in our team
If you're working on your local branch and haven't yet committed your changes, but you want to pull the latest code from the main branch for testing, you can use Git's stashing feature. Here are the steps:

Stash Your Changes:
First, you need to stash your changes. This can be done with the git stash command. This will save your uncommitted changes in a temporary area, allowing you to switch to another branch without disturbing your current work.
`git stash`

Switch to the main branch:
Now, you can safely switch to the main branch:
`git checkout main`

Pull the latest changes:
Next, you can pull the latest changes from the main branch:
`git pull`

Go back to your branch and apply your changes:
Once you're done testing on the main branch, you can switch back to your working branch and apply the changes you stashed earlier. This can be done with the git stash pop command, which applies the stashed changes and removes them from the stash.
`git checkout your-branch`
`git stash pop`

Note: These operations need to be done in your local git environment. If you have any questions or encounter any issues, you can refer to Git's official documentation or use git help <command> to get help information for a specific command.


## Standard usage
===================

    $ git checkout -b my-feature

... modify code ....

    $ git add <filename> 
    $ git commit -m “my feature is this”

... or, if you're lazy ...

    $ git commit -a -m "my feature is this"

... then fetch changes from master since we branched, and re-apply ours on top...

    $ git fetch
    $ git rebase master
    
... Also fine to merge here instead of rebase (but rebasing is better because makes it easier for others!). Resolve conflicts (if any) and add them ... 

    $ git add <filename>
    $ git rebase --continue

... # push my branch back to the server

    $ git push origin my-feature 

If you want to use git workflow to do code reviews (and are using github), at this point you can create a pull request. Using a pull request, you assign your buddy the task of approving merging your changes (from your feature branch back into master or a release branch). To create the pull request, go to your project on github.com, click "pull requests," then create.


## Other guy merges in the changes
===============================
(assuming no pull request)

    $ git fetch 

... list branches

    $ git branch -a

... bring a branch local

    $ git branch --track my-feature origin/my-feature
    $ git checkout master
    $ git merge my-feature

... resolve conflicts and look around ...

    $ git push

... delete branch (and remote branch) when done

    $ git branch -d my-feature 
    $ git push origin :my-feature 
    
If you used the github pull request workflow, at this point, the reviewer should delete the feature branch.

## Other useful commands
=====================

To remove remote branches from your list after they have been deleted by other people

    $ git remote prune origin
