#!/bin/bash

USER=controlm
USER_HOME=/home/controlm
AGENT_NAME=workbench-host
AGENT_PORT=7006
SERVER_PORT=7005
SERVER_HOST=workbench
SERVER_NAME=workbench
CONTAINER_NAME=workbench

EXIT_CODE=1
TRIES=0
MAX_TRIES=20

# Wait for workbench to complete startup
while [[ "${EXIT_CODE}" -ne "0" ]]; do
  docker logs ${CONTAINER_NAME} | grep "Completed"
  EXIT_CODE=$?
  if [[ "${EXIT_CODE}" -ne "0" ]]; then
    ((TRIES++))
    echo "Try ${TRIES}..."
    if [[ "${TRIES}" -le "${MAX_TRIES}" ]]; then
      sleep 30
    else
      echo "Error - exceeded max tries checking container ${CONTAINER_NAME}!"
      break
    fi
  fi
done

function Run_Agent_Test {

  cat > /tmp/agt_test.json <<EOF
{
    "TEST_AGENT_INSTALL": {
        "Type": "Folder",
        "testjob": {
            "Type": "Job:Command",
            "Command": "echo \"Hello from workbench\"",
            "Host": "${AGENT_NAME}",
            "RunAs": "${USER}"
        }
    }
}
EOF
  chmod +r /tmp/agt_test.json
  su - ${USER} bash -c ". ${USER_HOME}/venv/bin/activate && ctm env workbench::add"
  su - ${USER} bash -c ". ${USER_HOME}/venv/bin/activate && ctm run /tmp/agt_test.json"
  su - ${USER} bash -c ". ${USER_HOME}/venv/bin/activate && ctm env delete workbench" 
}

function Create_Silent_File {

    agent_port=$1
    server_port=$2
    server_host=$3
    server_name=$4

    cat > ${USER_HOME}/silent_install_agent.xml <<EOF
<AutomatedInstallation langpack="eng">
    <target.product>Control-M  Agent</target.product>
    <agent.parameters>
        <entry value="7035" key="ctm_agent.Tracker.Event.Port"/>
        <entry value="" key="ctm_agent.Force.Upgrade"/>
        <entry value="" key="Ignore.Disabling.Agent.Failure"/>
        <entry value="${agent_port}" key="field.Server.To.Agent.Port.Number"/>
        <entry value="${server_port}" key="field.Agent.To.Server.Port.Number"/>
        <entry value="${server_host}" key="field.Primary.Controlm.Server.Host"/>
        <entry value="${server_name}" key="field.Authorized.Controlm.Server.Host"/>
        <entry value="60" key="ctm_agent.Tcp_ip.Timeout"/>
    </agent.parameters>
</AutomatedInstallation>
EOF

}

function Run_Silent_Install {

    agent_name=$1

    cd ${USER_HOME}

    su - ${USER} bash -c "${USER_HOME}/setup.sh -silent ${USER_HOME}/silent_install_agent.xml"
    su - ${USER} bash -c '''source ~/.bashrc &&
        ctmcfg -table CONFIG -action update -parameter LOGICAL_AGENT_NAME -value ${agent_name} &
        ctmcfg -table CONFIG -action update -parameter PERSISTENT_CONNECTION -value Y &
        shut-ag -u controlm -p ALL &&
        start-ag -u controlm -p ALL'''

}


Create_Silent_File ${AGENT_PORT} ${SERVER_PORT} ${SERVER_HOST} ${SERVER_NAME}
Run_Silent_Install ${AGENT_NAME}
Run_Agent_Test

