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
                let output_table = [];
                for(let i = 0; i < data.length; i++){
                    output_table.push({
                        "value":{"plaintext": data[i]["value"], cellStyle: {
                            backgroundColor: data[i]["value"] === "useful" ? "green" : data[i]["value"] === "notuseful" ? "red" : "orange",
                                color: "white"
                            }},
                        "operator": {"plaintext": data[i]["operator"],  "copyIcon": true},
                        "name": {"plaintext": data[i]["file_data_enriched"]["name"]},
                        "magic_type": {"plaintext": data[i]["file_data_enriched"]["magic_type"]},
                        "nemesis type": {"plaintext": data[i]["file_data_enriched"]["nemesis_file_type"]},
                        "tags": {"plaintext": data[i]["file_data_enriched"]["tags"].join(", ")},
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
                                {"plaintext": "value", "type": "string", width: 70},
                                {"plaintext": "operator", "type": "string", width: 100},
                                {"plaintext": "name", "type": "string", fillWidth: true},
                                {"plaintext": "magic_type", "type": "string", "fillWidth": true},
                                {"plaintext": "nemesis_type", "type": "string", "width": 70},
                                {"plaintext": "tags", "type": "string", "fillWidth": true},
                                {"plaintext": "actions", "type": "button", "width": 70},
                            ],
                            "rows": output_table,
                            "title": "Triaged Files"
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