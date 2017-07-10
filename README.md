# HotMaps Toolbox
The toolbox will facilitate the following tasks on a spatially disaggregated level: 

1. Mapping heating and cooling energy situation including renewable and waste heat potentials in GIS layers,
2. Model the energy system, considering hourly matching of supply and demand, demand response etc.,
3. Supporting the comprehensive assessment of efficient heating and cooling according to the Energy Efficiency Directive,
4. Comparative assessment of supply and demand options and of given scenarios until 2050 regarding e.g. CO2-emissions, costs, share of renewables.


## HotMaps-building-hc web service
### Description
[description]

### Docker installation procedure
#### On Windows 10
Get Docker from [https://store.docker.com/editions/community/docker-ce-desktop-windows?tab=description](https://store.docker.com/editions/community/docker-ce-desktop-windows?tab=description)

Make sure Hyper-V is enabled.

#### On Mac OSX Yosemite 10.10.3+
Get Docker from [https://store.docker.com/editions/community/docker-ce-desktop-mac?tab=description](https://store.docker.com/editions/community/docker-ce-desktop-mac?tab=description)
#### On Windows 7 or Mac below OS X Yosemite 10.10.3
Get Docker Toolbox from [https://docs.docker.com/toolbox/overview/#whats-in-the-box](https://docs.docker.com/toolbox/overview/#whats-in-the-box)

Make sure you have VT-X/AMD-v enabled.

#### On Ubuntu 14.04+
Get Docker from [https://store.docker.com/editions/community/docker-ce-server-ubuntu?tab=description](https://store.docker.com/editions/community/docker-ce-server-ubuntu?tab=description)
#### On other systems or distributions
Get the installation procedure from [https://www.docker.com/get-docker](https://www.docker.com/get-docker)
### Running Docker image

Open a terminal (Docker Quickstart Terminal for Docker toolbox).

For docker toolbox (win7 / OS X below Yosemite) check that everything is working by running the following command:

`docker-machine ip` for docker toolbox (win7 / OS X below Yosemite)

This should return the IP of your active Docker machine that we will use later to connect to our web service (e.g. 192.168.99.100).

For other standard Docker setup run this command to check that it installed correctly `sudo docker --version`

Change directory to the *root* directory on this repository:

`cd my-git-directory`

Then run `sudo docker build -t hotmaps/building-hc .` (Sudo not needed if using Docker Toolbox.)

Then run `sudo docker run --name building-hc -p 9006:80 -d hotmaps/building-hc` (Sudo not needed if using Docker Toolbox.)

That's it! Now the web service should be up and running.

To check that everything is working, open a web browser and enter the IP of the Docker machine we retrieved above or localhost if not using docker-machine, **using port 9006**: http://*{your-docker-machine-ip}***:9006**/api

This should display the list of methods on your api.

Now you can put your own code in the "app" directory of this repository.

There is a backbone of the flask-api structure that you can use and adapt to your needs.

Note that wgsi.py is the entrypoint of your web service.