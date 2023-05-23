window.chartColors = {
    red: 'rgb(255, 99, 132)',
    orange: 'rgb(255, 159, 64)',
    yellow: 'rgb(255, 205, 86)',
    green: 'rgb(75, 192, 192)',
    blue: 'rgb(54, 162, 235)',
    purple: 'rgb(153, 102, 255)',
    grey: 'rgb(201, 203, 207)'
};

var timeInterval = 0; // Determines which dataset to display
var maxIntervals = 0;
var isSimRunning = false;
var intervalId;
var longestCallData = {};
var shortestCallData = {};

window.onload = function(){
    var sectorStatChart = document.getElementById('sectorStatChart').getContext('2d');
    var userCallChart = document.getElementById('userCallChart').getContext('2d');
    window.sectorStats = new Chart(sectorStatChart, sectorConfig);
    window.userCallChart = new Chart(userCallChart, userCallCfg);
    maxIntervals = hours*3600;

    document.getElementById('titleHours').innerHTML = hours;
    document.getElementById('titleUsers').innerHTML = users;
    document.getElementById('titleLength').innerHTML = length;
    document.getElementById('simBtn').addEventListener('click', () => toggleSimulation());
};

function toggleSimulation(){
    if(isSimRunning){
        clearInterval(intervalId);
        isSimRunning = false;
        document.getElementById('simBtnIcon').setAttribute("src", "./extras/play.png");
    }
    else{
        if(timeInterval >= maxIntervals){
            // Reset User call simulation graph
            timeInterval = 0;
            longestCallData = {};
            shortestCallData = {};
            document.getElementById('longestCallTime').innerHTML = 0;
            document.getElementById('shortestCallTime').innerHTML = 0;
            document.getElementById('longestCallId').innerHTML = "";
            document.getElementById('shortestCallId').innerHTML = "";
            userCallCfg.data.datasets[0].data = [{x: 0, y: Object.keys(userData[timeInterval]).length}];
            userCallCfg.data.labels = ['0'];
            window.userCallChart.update();
        }
        intervalId = setInterval(() => simulation(intervalId), 1);
        isSimRunning = true;
        document.getElementById('simBtnIcon').setAttribute("src", "./extras/pause.png");
    }
}

function simulation(id){
    if(timeInterval >= maxIntervals){
        // Auto stop at the end of data
        clearInterval(id);
        isSimRunning = false;
        document.getElementById('simBtnIcon').setAttribute("src", "./extras/play.png");
    }
    else{
        timeInterval += 1;

        sectorConfig.data.datasets[0].data = simData[timeInterval][0];
        sectorConfig.data.datasets[1].data = simData[timeInterval][1];
        window.sectorStats.update();

        if(timeInterval > 600){
            userCallCfg.data.datasets[0].data.shift()
            userCallCfg.data.labels.shift()
        }
        userCallCfg.data.datasets[0].data.push({ x: timeInterval, y: Object.keys(userData[timeInterval]).length});
        userCallCfg.data.labels.push(String(timeInterval));
        window.userCallChart.update();

        Object.keys(userData[timeInterval]).forEach(key => {
            if(Object.keys(longestCallData).length == 0){
                longestCallData = {
                    'id': key,
                    'callTime': userData[timeInterval][key].callTimeLeft
                }
            }
            if(Object.keys(shortestCallData).length == 0){
                shortestCallData = {
                    'id': key,
                    'callTime': userData[timeInterval][key].callTimeLeft
                }
            }
            if(userData[timeInterval][key].callTimeLeft > longestCallData.callTime){
                longestCallData = {
                    'id': key,
                    'callTime': userData[timeInterval][key].callTimeLeft
                }
            }
            if(userData[timeInterval][key].callTimeLeft < shortestCallData.callTime){
                shortestCallData = {
                    'id': key,
                    'callTime': userData[timeInterval][key].callTimeLeft
                }
            }
        });
        if(timeInterval%10 == 0){
            document.getElementById('longestCallTime').innerHTML = Math.floor(longestCallData.callTime+1);
            document.getElementById('shortestCallTime').innerHTML = Math.floor(shortestCallData.callTime+1);
            document.getElementById('longestCallId').innerHTML = longestCallData.id;
            document.getElementById('shortestCallId').innerHTML = shortestCallData.id;
        }
    }
}

var sectorConfig = {
    type: 'line',
    data: {
        labels: ['Call attempts', 'Call Successful', 'Handoff attempts', 'Handoffs successful', 'Handoffs failed'],
        datasets: [{
            label: 'Alpha sector',
            data: simData[timeInterval][0],
            fill: false,
            borderColor: window.chartColors.red,
            backgroundColor: window.chartColors.red,
        }, {
            label: 'Bela sector',
            data: simData[timeInterval][1],
            fill: false,
            borderColor: window.chartColors.blue,
            backgroundColor: window.chartColors.blue
        }]
    },
    options: {
        plugins: {
            title: {
                display: true,
                text: 'Sector stats'
            }
        },
        animation: {
            duration: 1
        }
    }
};

var userCallCfg = {
    type: 'line',
    data: {
        datasets: [{
            label: 'Number of users currently on call (10 minute window)',
            data: [{x: 0, y: Object.keys(userData[timeInterval]).length}],
            lineTension: 0,
            fill: false,
            pointRadius: 0,
            borderColor: window.chartColors.red,
            backgroundColor: window.chartColors.red,
        }],
        labels: ['0']
    },
    options: {
        plugins: {
            title: {
                display: true,
                text: 'Users on call'
            }
        },
        scales: {
            y: {
                beginAtZero: true,
                min: 0,
                max: 20,
            }
        },
        animation: {
            duration: 1
        }
    }
};
