$('#is-manager').change(function(){
    $('#is-manager-div').toggleClass('placeholder');
    $('#is-manager-div').toggleClass('checked');
});

$(".octicon").mouseenter(function(e){
    $(this).toggleClass("octicon-blue");
});
$(".octicon").mouseleave(function(e){
    $(this).toggleClass("octicon-blue");
});

select_valid_flag = true;
function change_span_html(){
    if (select_valid_flag){
        $("#cargo").addClass("valid");
        select_valid_flag = false;
    }
    //setTimeout(function(){
    $('.select-value#span-cargo').html($('#cargo option:selected').text());
    //}, 70);
    
}

var expanded = false;
var options = document.getElementById("selectOptions");
var select = $('.select-multiselect');


document.addEventListener("click", function(event) {
    // If user clicks inside the element, do nothing
    if(event.target.classList[0] == "selectWrapper"){
        select.toggleClass('multiselect-collapsed');
        if (!expanded) {
            options.style.display = "block";
            expanded = true;
        } else {
            options.style.display = "none";
            expanded = false;
        }
    }else if(event.target.classList[0] == "singleOption" || event.target.classList[0] == "singleOptionInput"){
        return;
    }else if (expanded) {
        select.toggleClass('multiselect-collapsed');
        options.style.display = "none";
        expanded = false;
    }
    console.log(event.target.classList)
});

$( function() {
    $.each($(".datepicker"), function(i,l){
        var aux = $(l).val();
        $(l).datepicker( {
            monthNames: [ "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro" ],
            monthNamesShort: [ "Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez" ],
            dateFormat: "dd/mm/yy",
            changeMonth: true,
            changeYear: true,
            currentText: "Hoje",
            closeText: "Pronto",
            showButtonPanel: true,
            onClose: function(dateText, inst) {
                
                
                function isDonePressed(){
                    return ($('#ui-datepicker-div').html().indexOf('ui-datepicker-close ui-state-default ui-priority-primary ui-corner-all ui-state-hover') > -1);
                }
                
                if (isDonePressed()){
                    var month = $("#ui-datepicker-div .ui-datepicker-month :selected").val();
                    var year = $("#ui-datepicker-div .ui-datepicker-year :selected").val();
                    $(this).datepicker('setDate', new Date(year, month, 1)).trigger('change');
                    
                    $('.date-picker').focusout()//Added to remove focus from datepicker input box on selecting date
                }
            },
            beforeShow : function(input, inst) {
                
                inst.dpDiv.addClass('month_year_datepicker')
                
                if ((datestr = $(this).val()).length > 0) {
                    year = datestr.substring(datestr.length-4, datestr.length);
                    month = datestr.substring(0, 2);
                    $(this).datepicker('option', 'defaultDate', new Date(year, month-1, 1));
                    $(this).datepicker('setDate', new Date(year, month-1, 1));
                    $(".ui-datepicker-calendar").hide();
                }
            }
        });
        $(l).val(aux);
    });
    
    $.each($(".meta-value"), function(i,l){
        var aux = $(l).val();
        aux = aux.replace(".", ",");
        $(l).val(aux);
    });
});

select_valid_flag = true;
function change_span_html(){
    if (select_valid_flag){
        $("#resource-select").addClass("valid");
        select_valid_flag = false;
    }
    $('.select-value#span-resource').html($('#resource-select option:selected').text());
}

function parse_date(datestring) {
    datearr = datestring.split('/')
    return new Date(datearr[2], datearr[1]-1, datearr[0])
}

function submit_allocation() {
    var error_log = 'Erros: \n';
    var valid = true;

    // start_date = $('#start-date').val().split('/')
    // start_date = new Date(start_date[2], start_date[1]-1, start_date[0])
    start_date = parse_date($('#start-date').val())
    // end_date = $('#end-date').val().split('/')
    // end_date = new Date(end_date[2], end_date[1]-1, end_date[0])
    end_date = parse_date($('#end-date').val())
    now = new Date()
    today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
    if (start_date > end_date) {
        valid = false;
        error_log += "- A data de término não deve ser anterior à data de início\n";
    } else if (end_date < today) {
        valid = false;
        error_log += "- Você não pode reservar recursos para datas passadas";
    }
    
    

    if (valid) {
        $('#add-allocation-form').submit();
    } else {posterior
        alert(error_log);
    }
}

var allocations = [];
{% for allocation in allocations %}
allocations.push({
    resource: "{{allocation.resource}}",
    activity: "{{allocation.activity}}",
    start_date: parse_date("{{ allocation.start_date|date:'d/m/Y' }}"),
    end_date: parse_date("{{ allocation.end_date|date:'d/m/Y' }}")
})
{% endfor %}

function is_resource_available(resource, start_date, end_date) {
    available = true;

    for (var i=0; i<allocations.length; i++) {
        if (allocations[i].resource == resource) {
            alloc_start = allocations[i].start_date
            alloc_end = allocations[i].end_date
            if (start_date >= alloc_start && start_date <= alloc_end) {
                available = false;
            } else if (end_date >= alloc_start) {
                available = false;
            }
        }
    }

    return available
}

// $('#add-allocation-form').submit(function(event){
//     event.preventDefault();

//     alert("hey!");

//     var error_log = 'Erros: \n';
//     var valid = true;

//     start_date = Date($('#start-date').val())
//     end_date = Date($('#end-date').val())
//     if (start_date > end_date) {
//         valid = false;
//         error_log += "- A data de término deve ser posterior à data de início\n";
//     }

//     if (!valid) {
//         alert(error_log);
//     } else {
//         $(this).unbind('submit').submit();
//     }
//     return valid
// });

// $('#btn-add-allocation').on("submit", function(event){
//     event.preventDefault();

//     alert("hey!");

//     var error_log = 'Erros: \n';
//     var valid = true;

//     start_date = Date($('#start-date').val())
//     end_date = Date($('#end-date').val())
//     if (start_date > end_date) {
//         valid = false;
//         error_log += "- A data de término deve ser posterior à data de início\n";
//     }
    
//     if (!valid) {
//         alert(error_log);
//     } else {
//         $(this).unbind('submit').submit();
//     }
//     return valid
// });
