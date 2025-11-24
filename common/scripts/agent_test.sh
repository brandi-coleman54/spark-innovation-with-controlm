#!/bin/bash

CTM_SERVER=$1
CTM_AGENT=$2

function Test_Agent {

    ctm_server=$1
    ctm_agent=$2

    count=1
    limit=50
    while [ "${count}" -le "${limit}" ]; do

        echo "Agent ${ctm_agent} test ${count}"
        ctm config server:agent::test ${ctm_server} ${ctm_agent}
        if [ "$?" -eq "0" ]; then
            break
        else
            ((count++))
            if [[ "${count}" -gt "${limit}" ]]; then
                echo "Timed out waiting for agent to become available"
            else
                sleep 10
            fi
        fi
        
    done

}

Test_Agent ${CTM_SERVER} ${CTM_AGENT}
