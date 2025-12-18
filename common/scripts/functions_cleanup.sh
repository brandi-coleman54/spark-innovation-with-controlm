#!/usr/bin/env bash

function Delete_TD_User {
    user=$1
    
    echo "Deleting user ${user} and API Tokens created by user ${user}"
    ctm config authorization:user::delete ${user} -s "deleteUserTokens=true"
    if [ $? -ne 0 ]; then
        echo "There was a problem deleting user ${user}"
    fi
}

function Delete_API_Token {
    token=$1

    echo "Deleting API Token ${token}"
    ctm auth token::delete ${token}
    if [ $? -ne 0 ]; then
        echo "There was a problem deleting Token ${token}"
    fi 
}

function Delete_TD_Role {
    role=$1
    
    echo "Deleting role ${role}"
    ctm config authorization:role::delete ${role}
    if [ $? -ne 0 ]; then
        echo "There was a problem deleting role ${role}"
    fi 
}

function Delete_HostGroup {
    hg=$1
    
    echo "Deleting HostGroup ${hg}"
    ctm config server:hostgroup::delete IN01 ${hg}
    if [ $? -ne 0 ]; then
        echo "There was a problem deleting HostGroup ${hg}"
    fi
}

function Delete_Agents {
    code=$1
    
    echo "Deleting Agents for ${code}"
    agents=$(ctm config server:agents::get IN01 -s "agent=${code}*" | jq -r '.agents[].nodeid')
    for agent in ${agents[@]}; do
        ctm config server:agent::delete IN01 ${agent}
        if [ $? -ne 0 ]; then
            echo "There was a problem deleting agent ${agent}"
        fi
    done
}

function Delete_CCPs {

    code=$1

    echo "Deleteing Connection Profiles for ${code}"
    ccps=$(ctm deploy connectionprofiles:centralized:status::get -s "type=*&name=${code}*" | jq -r '.statuses[].name')
    for ccp in ${ccps[@]}; do
        type=$(ctm deploy connectionprofiles:centralized::get -s "type=*&name=${ccp}" | jq -r ".${ccp}.Type")
        short_type=${type#*:}
        ctm deploy connectionprofile:centralized::delete "${short_type}" ${ccp}
    done 
}

function Delete_Folders {
    
    code=$1

    echo "Deleting Folders for ${code}"
    folders=$(ctm deploy folders::get -s "server=IN01&folder=${code}*" | jq -r 'keys[]')
    for folder in ${folders[@]}; do
        ctm deploy folder::delete IN01 ${folder}
    done
}

function Add_User_Role {

    user=$1
    role=$2

    ctm config authorization:user::get "${user}" | jq ".Roles += [\"${role}\"]" > /tmp/user_upd.json
    ctm config authorization:user::update "${user}" /tmp/user_upd.json

}

function Remove_User_Role {

    user=$1
    role=$2

    ctm config authorization:user::get ${user} | jq "del(.Roles[] | select(. == \"${role}\"))" > /tmp/user_upd.json
    ctm config authorization:user::update "${user}" /tmp/user_upd.json

}
