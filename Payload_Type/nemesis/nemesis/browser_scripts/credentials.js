function(task, responses){
    if(task.status.includes("error")){
        const combined = responses.reduce( (prev, cur) => {
            return prev + cur;
        }, "");
        return {'plaintext': combined};
    }else if(task.completed){
        if(responses.length > 0){
            try{
                let data = JSON.parse(responses[0]);
                data = data["nemesis_authentication_data"];
                let output_table = [];
                for(let i = 0; i < data.length; i++){
                    output_table.push({
                        "type":{"plaintext": data[i]["type"]},
                        "timestamp": {"plaintext": data[i]["timestamp"]},
                        "username": {"plaintext": data[i]["username"] },
                        "data": {"plaintext": data[i]["data"]},
                        "uri": {"plaintext": data[i]["uri"]},
                        "notes": {"plaintext": data[i]["notes"]},
                        "actions": {"button": {
                                "name": "Actions",
                                "type": "menu",
                                "value": [
                                    {
                                        "name": "View All Data",
                                        "type": "dictionary",
                                        "value": data[i],
                                        "leftColumnTitle": "Key",
                                        "rightColumnTitle": "Value",
                                        "title": "Viewing Credential Data"
                                    },
                                ]
                            }},
                    });
                }
                return {
                    "table": [
                        {
                            "headers": [
                                {"plaintext": "type", "type": "string", width: 100},
                                {"plaintext": "timestamp", "type": "date", width: 100},
                                {"plaintext": "username", "type": "string", fillWidth: true},
                                {"plaintext": "data", "type": "string", fillWidth: true},
                                {"plaintext": "uri", "type": "string", fillWidth: true},
                                {"plaintext": "notes", "type": "string", fillWidth: true},
                                {"plaintext": "actions", "type": "button", "width": 70},
                            ],
                            "rows": output_table,
                            "title": "Collected Credential Material"
                        }
                    ]
                }
            }catch(error){
                console.log(error);
                const combined = responses.reduce( (prev, cur) => {
                    return prev + cur;
                }, "");
                return {'plaintext': combined};
            }
        }else{
            return {"plaintext": "No output from command"};
        }
    }else{
        return {"plaintext": "No data to display..."};
    }
}