$('.slider').slick({
    arrows: false,
    dots: false,
    slidesToShow: 7,
    autoplay: true,
    autoplaySpeed: 2000,
     responsive: [
        {
            breakpoint: 992,
            settings: {
                slidesToShow: 5,
            }
        },
         {
            breakpoint: 500,
            settings: {
                slidesToShow: 4,
            }
        },
         {
            breakpoint: 370,
            settings: {
                slidesToShow: 3,
            }
        },

    ]
});
$('.slider_review').slick({
    infinite: true,
    slidesToShow: 3,
    slidesToScroll: 1,
    arrows: true,
    responsive: [
        {
            breakpoint: 1200,
            settings: {
                slidesToShow: 2,
            }
        },
        {
            breakpoint: 768,
            settings: {
                slidesToShow: 1,
            }
        }
    ]
});



