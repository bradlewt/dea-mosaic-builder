project = "DEA Mosaic Builder"
project_copyright = "%Y, Joel Rhine"
author = "Joel Rhine"

html_theme = "furo"

html_static_path = ["_static"]
templates_path = ["_templates"]

html_theme_options = {
    "sidebar_hide_name": True,
    "light_logo": "rwd-header-light.png",
    "dark_logo": "rwd-header-dark.png",
    "source_repository": "https://github.com/rhinejoel/dea-mosaic-builder",
    "source_branch": "main",
    "source_directory": "docs/source/",
    "footer_icons": [
        {
            "name": "GitHub",
            "url": "https://github.com/rhinejoel/dea-mosaic-builder",
            "html": "",
            "class": "fa-brands fa-solid fa-github",
        },
        {
            "name": "LinkedIn",
            "url": "https://www.linkedin.com/in/joel-rhine",
            "html": "",
            "class": "fa-brands fa-linkedin",
        },
        {
            "name": "Email",
            "url": "mailto:joelrhine7@gmail.com?subject=Mosaic Builder Docs",
            "html": "",
            "class": "fa-solid fa-envelope",
        },
    ],
}
html_css_files = [
    "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/fontawesome.min.css",
    "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/solid.min.css",
    "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/brands.min.css",
]
