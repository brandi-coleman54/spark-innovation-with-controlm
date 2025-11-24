#!/bin/bash

CTM_SERVER=$1
CTM_AGENT=$2

function Test_Agent {

    ctm_server=$1
    ctm_agent=$2

    count=1
    limit=20
    while [ "${count}" -le "${limit}" ]; do

        echo "Agent ${ctm_agent} test ${count}"
        status=$(ctm config server:agents::get ${ctm_server} -s "agent=${ctm_agent}" | jq -r '.agents[0].status')
        if [[ "${status}" == "Available" ]]; then
            break
        else
            ((count++))
            if [[ "${count}" -gt "${limit}" ]]; then
                echo "Timed out waiting for agent to become available"
            else
                sleep 10
            fi
        fi
        echo "Status is ${status}"
        
    done

}

Test_Agent ${CTM_SERVER} ${CTM_AGENT}
