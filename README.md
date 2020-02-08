# Frame.io Custom Action driven automated slate rendering

# Frame.io Setup

1. Create a new Custom Action via the developer portal
2. Setup a new subdomain to use for your Custom Action receiver (yourwebhook.io for example)
3. Point the Custom Action at your subdomain and endpoint (http://yourwebhook.io/new)

# Setup

1. Setup an Ubuntu instance on AWS
2. Expose port 8000 via the Security Groups settings for this instance
3. Install docker and docker-compose
4. Export an ENV variable called `FRAMEIO_TOKEN` 
5. `git clone` this repository
6. Run `docker-compose build` followed by `docker-compose up` from within the cloned directory to start the infrastructure and API endpoint

# TODO

1. Add support for version stacks
2. Update slate to add space for more fields (FPS, resolution, etc.)
3. Fix slate so that it counts down correctly!!!
