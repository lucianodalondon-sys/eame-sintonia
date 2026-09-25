jQuery(document).ready(function($){

	//Main menu
	$('#main-menu').smartmenus();
	
	//Mobile menu toggle
	$('.navbar-toggle').click(function(){
		$('.region-primary-menu').slideToggle();
	});

	//Mobile dropdown menu
	if ( $(window).width() < 767) {
		$(".region-primary-menu li a:not(.has-submenu)").click(function () {
			$('.region-primary-menu').hide();
	    });
	}

	var interval= 500;

	$('.field-content a').each(function(index) {
	  /*if (index < 1) 
	  	$(this).addClass('blinkingLink');*/
	});

	$.fn.blink = function(options) {
	  var defaults = {
	    interval: 500 // intervallo di lampeggio in millisecondi
	  };
	  
	  var settings = $.extend({}, defaults, options);

	  return this.each(function() {
	    var $this = $(this);
	    var currentIndex = 0;
	    var colors = ["red", "#078D92"];
	    
	    setInterval(function() {
	      currentIndex = (currentIndex + 1) % 2;
	      $this.css('color', colors[currentIndex]); 
	      
	      $this.css('color', colors[currentIndex]); 	
	      
	      /*if ($this.css('visibility')=='visible')
	      	 $this.css('visibility', 'hidden');
	      else
	      	$this.css('visibility', 'visible');	*/
	      
	    }, settings.interval);
	  });
	};
	  
	$('.blinkingLink').blink();
});