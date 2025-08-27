FROM jenkins/jenkins:lts

# Switch to root to install dependencies
USER root

# Install Docker CLI and OpenJDK 17
RUN apt-get update && apt-get install -y \
    docker.io \
    openjdk-17-jdk \
    && rm -rf /var/lib/apt/lists/*

# Install suggested plugins
COPY plugins.txt /usr/share/jenkins/ref/plugins.txt
RUN jenkins-plugin-cli --plugin-file /usr/share/jenkins/ref/plugins.txt

# Configure Jenkins to skip setup wizard
ENV JAVA_OPTS -Djenkins.install.runSetupWizard=false

# Expose Jenkins port
EXPOSE 8080

# Switch back to Jenkins user
USER jenkins