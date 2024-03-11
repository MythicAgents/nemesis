<p align="center">
    <img src="agent_icons/nemesis.svg" alt="Nemesis" style="width: 100px;" />
</p>
<hr />

# nemesis

This is a Mythic agent for interacting with the 3rd party service, [Nemesis](https://github.com/SpecterOps/Nemesis).

This doesn't build a payload, but instead generates a "callback" within Mythic that allows you to interact with Nemesis's API. 

Once you have Nemesis running, set your basic auth values as NEMESIS_USERNAME and NEMESIS_PASSWORD as user secrets in the Mythic UI (red key on your operator settings page).

## How to install an agent in this format within Mythic

When it's time for you to test out your install or for another user to install your agent, it's pretty simple. Within Mythic you can run the `mythic-cli` binary to install this in one of three ways:

* `sudo ./mythic-cli install github https://github.com/user/repo` to install the main branch
* `sudo ./mythic-cli install github https://github.com/user/repo branchname` to install a specific branch of that repo
* `sudo ./mythic-cli install folder /path/to/local/folder/cloned/from/github` to install from an already cloned down version of an agent repo

Now, you might be wondering _when_ should you or a user do this to properly add your agent to their Mythic instance. There's no wrong answer here, just depends on your preference. The three options are:

* Mythic is already up and going, then you can run the install script and just direct that agent's containers to start (i.e. `sudo ./mythic-cli start agentName` and if that agent has its own special C2 containers, you'll need to start them too via `sudo ./mythic-cli start c2profileName`).
* Mythic is already up and going, but you want to minimize your steps, you can just install the agent and run `sudo ./mythic-cli start`. That script will first _stop_ all of your containers, then start everything back up again. This will also bring in the new agent you just installed.
* Mythic isn't running, you can install the script and just run `sudo ./mythic-cli start`.

## Documentation

View the rendered documentation by clicking on **Docs -> Agent Documentation** in the upper right-hand corner of the Mythic interface.