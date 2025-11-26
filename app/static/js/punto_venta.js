document.addEventListener("DOMContentLoaded", () => {
    let sidebar = document.querySelector(".sidebar");
    let closeBtn = document.querySelector("#btn");
    const mainContent = document.querySelector(".ml-20, .lg\\:ml-64");

    // Variable para trackear el estado manual del sidebar
    let isManuallyCollapsed = false;
    
    // Función para togglear la sidebar manualmente
    function toggleSidebar() {
        const logoName = document.querySelector(".logo_name");
        const subtitle = document.querySelector(".text-xs.text-pink-200");
        const linksNames = document.querySelectorAll(".links_name");
        const navLinks = document.querySelectorAll(".nav-list a");
        const headerFlex = document.querySelector(".flex.items-center");
        
        if (!isManuallyCollapsed) {
            // Colapsar manualmente - forzar estado colapsado incluso en desktop
            sidebar.classList.remove("lg:w-64");
            sidebar.classList.add("w-20");
            closeBtn.classList.replace("bx-menu", "bx-menu-alt-right");
            
            // Ocultar textos
            if (logoName) {
                logoName.classList.remove("lg:block");
                logoName.classList.add("hidden");
            }
            if (subtitle) {
                subtitle.classList.remove("lg:block");
                subtitle.classList.add("hidden");
            }
            linksNames.forEach(link => {
                link.classList.remove("lg:inline");
                link.classList.add("hidden");
            });
            
            // Centrar iconos
            navLinks.forEach(link => {
                link.classList.remove("lg:p-3", "lg:justify-start");
                link.classList.add("p-2", "justify-center");
            });
            
            // Centrar botón del menú
            if (headerFlex) {
                headerFlex.classList.remove("lg:justify-between");
                headerFlex.classList.add("justify-center");
            }
            
            // Ajustar contenido principal
            if (mainContent) {
                mainContent.classList.remove("lg:ml-64");
                mainContent.classList.add("ml-20");
            }
            
            isManuallyCollapsed = true;
            
        } else {
            // Expandir manualmente - restaurar comportamiento responsive
            sidebar.classList.remove("w-20");
            sidebar.classList.add("lg:w-64");
            closeBtn.classList.replace("bx-menu-alt-right", "bx-menu");
            
            // Restaurar textos responsive
            if (logoName) {
                logoName.classList.remove("hidden");
                logoName.classList.add("lg:block");
            }
            if (subtitle) {
                subtitle.classList.remove("hidden");
                subtitle.classList.add("lg:block");
            }
            linksNames.forEach(link => {
                link.classList.remove("hidden");
                link.classList.add("lg:inline");
            });
            
            // Restaurar iconos responsive
            navLinks.forEach(link => {
                link.classList.remove("p-2", "justify-center");
                link.classList.add("lg:p-3", "lg:justify-start");
            });
            
            // Restaurar header responsive
            if (headerFlex) {
                headerFlex.classList.remove("justify-center");
                headerFlex.classList.add("lg:justify-between");
            }
            
            // Restaurar contenido responsive
            if (mainContent) {
                mainContent.classList.remove("ml-20");
                mainContent.classList.add("lg:ml-64");
            }
            
            isManuallyCollapsed = false;
        }
    }

    // Event listener para el botón de toggle
    if (closeBtn) {
        closeBtn.addEventListener("click", toggleSidebar);
    }
});