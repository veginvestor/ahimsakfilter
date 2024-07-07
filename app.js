// Google Drive URLs for the CSV files
const equityListUrl = 'https://api.allorigins.win/get?url=' + encodeURIComponent('https://drive.google.com/uc?export=download&id=1gqVWNcOkAX9sn2icc2jU9qomN0Jpmfsn');
const ahimsakListUrl = 'https://api.allorigins.win/get?url=' + encodeURIComponent('https://drive.google.com/uc?export=download&id=13QfE7MqQxBavedhPmYPXamxIf09PpAYd');

// Quotes for motivation
const quotes = [
    "Investing ethically is the first step towards a cruelty-free world.",
    "Your financial decisions can save lives. Choose cruelty-free investments.",
    "Every rupee you invest has the power to change the world. Invest in kindness."
];

let equityList = [];
let ahimsakList = [];
let progressBarWidth = 0;

// Function to fetch and parse CSV data
function fetchCSV(url) {
    return new Promise((resolve, reject) => {
        $.get(url, function(response) {
            const base64Index = response.contents.indexOf('base64,') + 'base64,'.length;
            const decodedData = atob(response.contents.substring(base64Index));

            Papa.parse(decodedData, {
                header: true,
                complete: function(results) {
                    resolve(results.data);
                },
                error: function(error) {
                    reject(error);
                }
            });
        }).fail(function(error) {
            reject(error);
        });
    });
}

// Function to normalize company names
function normalizeCompanyName(name) {
    if (!name) return '';
    return name.trim().replace(/\.$/, '').toLowerCase();
}

// Function to convert string to camel case
function toCamelCase(str) {
    return str.replace(/\b\w/g, char => char.toUpperCase());
}

// Function to show motivational quotes one by one
function showQuotesOneByOne() {
    let index = 0;
    $('#quotes').show();
    const interval = setInterval(() => {
        $('#quotes').empty().append('<div class="quote">' + quotes[index] + '</div>').fadeIn();
        index++;
        if (index === quotes.length) {
            index = 0;
        }
    }, 3000);

    return interval;
}

// Function to hide the quotes
function hideQuotes() {
    $('#quotes').fadeOut();
}

// Function to show the input container
function showInput() {
    $('#input-container').fadeIn();
}

// Function to update the progress bar
function updateProgressBar() {
    progressBarWidth += 10;
    $('#progress-bar').width(progressBarWidth + '%');
}

// Function to handle company selection and display results
function handleCompanySelection(companyName) {
    const ahimsakData = ahimsakList.find(company => company['Company Name'] === companyName);

    // Clear all previous background classes
    $('#results').removeClass('green-background red-background grey-background color-transform');

    if (ahimsakData) {
        $('#company-name').text(`Company Name: ${toCamelCase(ahimsakData['Company Name'])}`);
        $('#industry').text(`Industry: ${ahimsakData['Industry']}`);
        $('#category').text(`Category: ${ahimsakData['Category']}`);

        if (ahimsakData['Category'].toLowerCase() === 'green') {
            $('#results').addClass('green-background');
            $('.particles').addClass('green-particles').removeClass('red-particles');
        } else if (ahimsakData['Category'].toLowerCase() === 'red') {
            $('#results').addClass('red-background');
            $('.particles').addClass('red-particles').removeClass('green-particles');
        }
    } else {
        $('#company-name').text('Sorry, this company is not categorized by AIM. We will review it and update our records.');
        $('#industry').text('');
        $('#category').text('');
        $('#results').addClass('grey-background');
    }

    $('#results').show();
}

$(document).ready(async function() {
    try {
        // Initialize quotes and progress bar animations
        const quoteInterval = showQuotesOneByOne();
        $('#progress-bar').show();

        const progressBarInterval = setInterval(updateProgressBar, 500);

        // Fetch and parse CSV files
        equityList = await fetchCSV(equityListUrl);
        ahimsakList = await fetchCSV(ahimsakListUrl);

        // Normalize and filter company names
        equityList = equityList.filter(company => company['NAME OF COMPANY']).map(company => ({
            ...company,
            'NAME OF COMPANY': normalizeCompanyName(company['NAME OF COMPANY'])
        }));

        ahimsakList = ahimsakList.filter(company => company['Company Name']).map(company => ({
            ...company,
            'Company Name': normalizeCompanyName(company['Company Name'])
        }));

        // Stop animations
        clearInterval(quoteInterval);
        clearInterval(progressBarInterval);

        // Hide quotes and progress bar, show input field
        hideQuotes();
        $('#progress-bar').fadeOut();
        showInput();

        // Handle input and suggestions
        $('#company').on('input', function() {
            const query = normalizeCompanyName($(this).val());

            $('#suggestions').empty();
            if (query.length > 0) {
                const suggestions = equityList.filter(company => company['NAME OF COMPANY'].includes(query)).slice(0, 10);

                suggestions.forEach(item => {
                    $('#suggestions').append('<a href="#" class="list-group-item list-group-item-action suggestion-item">' + toCamelCase(item['NAME OF COMPANY']) + '</a>');
                });
            }
        });

        // Handle suggestion clicks
        $(document).on('click', '.suggestion-item', function() {
            const companyName = normalizeCompanyName($(this).text());
            $('#suggestions').empty(); // Clear suggestions on click
            handleCompanySelection(companyName);
        });

        // Handle Enter key press
        $('#company').on('keypress', function(event) {
            if (event.key === 'Enter') {
                const companyName = normalizeCompanyName($(this).val());
                $('#suggestions').empty(); // Clear suggestions on Enter
                handleCompanySelection(companyName);
            }
        });
    } catch (error) {
        console.error('Error during initialization:', error);
    }
});
