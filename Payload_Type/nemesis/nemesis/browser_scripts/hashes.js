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
                data = data["nemesis_extracted_hashes"];
                let output_table = [];
                for(let i = 0; i < data.length; i++){
                    output_table.push({
                        "hash_type":{"plaintext": data[i]["hash_type"]},
                        "hash_value": {"plaintext": data[i]["hash_value"],  "copyIcon": true},
                        "cracked": {"plaintext": data[i]["is_cracked"] ? "true": "false"},
                        "plaintext": {"plaintext": data[i]["plaintext_value"]},
                        "cracker": {"plaintext": data[i]["is_submitted_to_cracker"] ? "Submitted" : "Not Submitted"},
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
                                        "title": "Viewing Objective Data"
                                    },
                                ]
                            }},
                    });
                }
                return {
                    "table": [
                        {
                            "headers": [
                                {"plaintext": "hash_type", "type": "string", width: 100},
                                {"plaintext": "hash_value", "type": "string", fillWidth: true},
                                {"plaintext": "cracked", "type": "string", "width": 100},
                                {"plaintext": "plaintext", "type": "string", "fillWidth": true},
                                {"plaintext": "cracker", "type": "string", "width": 70},
                                {"plaintext": "actions", "type": "button", "width": 70},
                            ],
                            "rows": output_table,
                            "title": "Collected Hashes"
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