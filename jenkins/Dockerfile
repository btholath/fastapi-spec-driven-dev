FROM jenkins/jenkins:lts-jdk17

USER root

# Base tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    gnupg \
    git \
    python3-venv \
    python3-pip \
 && rm -rf /var/lib/apt/lists/*

# Add Docker’s official apt repo and install docker-ce-cli
RUN install -m 0755 -d /etc/apt/keyrings \
 && curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg \
 && chmod a+r /etc/apt/keyrings/docker.gpg \
 && echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian \
    $(. /etc/os-release && echo $VERSION_CODENAME) stable" > /etc/apt/sources.list.d/docker.list \
 && apt-get update \
 && apt-get install -y --no-install-recommends docker-ce-cli \
 && rm -rf /var/lib/apt/lists/*

# Jenkins env
ENV JAVA_OPTS="-Djenkins.install.runSetupWizard=false" \
    JENKINS_UC="https://updates.jenkins.io" \
    JENKINS_UC_EXPERIMENTAL="https://updates.jenkins.io/experimental"

# Plugins
COPY plugins.txt /usr/share/jenkins/ref/plugins.txt
RUN jenkins-plugin-cli --verbose --latest=false --plugin-file /usr/share/jenkins/ref/plugins.txt

EXPOSE 8080 50000
USER jenkins
