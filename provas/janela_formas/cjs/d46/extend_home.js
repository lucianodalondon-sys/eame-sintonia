jQuery(document).ready(function($){

	if ($(".previsione-pittorica-img").length) {
		var d = new Date();
		var n = d.getHours();
		var step = 0;
		var step_pittorica = 6;
		if ( n<=3 ) {
			step = 3;
			step_pittorica = 6;
		} else if (n>3 && n<=6) {
			step = 6;
			step_pittorica = 6;
		} else if (n>6 && n<=9) {
			step = 9;
			step_pittorica = 12;
		} else if (n>9 && n<=12) {
			step = 12;
			step_pittorica = 12;
		} else if (n>12 && n<=15) {
			step = 15;
			step_pittorica = 18;
		} else if (n>15 && n<=18) {
			step = 18;
			step_pittorica = 18;
		} else if (n>18 && n<=21) {
			step = 21;
			step_pittorica = 24;
		} else if (n>21 && n<=24) {
			step = 24;
			step_pittorica = 24;
		}

		var day = d.getDate();
		if (day<=9) {
			day = "0"+day;
		}
		var month = d.getMonth() + 1;
		if (month<=9) {
			month = "0"+month;
		}
		var year = d.getFullYear();
		var data = day+"-"+month+"-"+year;


		if (step<=9) {
			step_disagio = "0"+step;
		} else {
			step_disagio = step;
		}

		var previsione_pittorica_src = "http://93.56.31.72/meteopuglia/images/meteo/today-"+step_pittorica+".jpg";
		//var previsione_meteo_puglia_src = "http://wwwold.agrometeopuglia.it/opencms/imgLami/thumbs/PUGLIA_pugtmp_"+data+"_"+step+".png";
		var mappa_disagio_src = "http://wwwold.agrometeopuglia.it/opencms/imgIndiceDisagio/PUGLIADIS_pugwchill_"+data+"_"+step_disagio+".png";
		var mappa_temperatura_src = "/image/MappePrevisione/Temperatura/PUGLIA_pugtmp_"+data+"_"+step_disagio+".png";  


		$(".previsione-pittorica-img").attr("src", previsione_pittorica_src);
		//$(".previsione-meteo-puglia-img").attr("src", previsione_meteo_puglia_src);
		$(".mappa-disagio-img").attr("src", mappa_disagio_src);
		$(".mappa-temperatura").attr("src", mappa_temperatura_src);
		
		$.get({
		  cache: false,
		  url: '/bollettino-elettronico/LastSendEmail.txt', 	  
		}).then(function(theUrlBoll){
		  var theUrl="."+theUrlBoll; 
		  $(".bollettino").attr("href", theUrl);
		});
		
	}	
});
