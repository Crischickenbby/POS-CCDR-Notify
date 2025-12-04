/**
 * 🎨 CONFIGURACIÓN DE TAILWIND CSS PARA BLANCOS VALENTINA
 * 
 * Este archivo le dice a Tailwind:
 * - Dónde buscar las clases CSS en tu proyecto
 * - Qué personalizaciones agregar (colores, fuentes, etc.)
 * - Qué plugins usar
 * 
 * 📚 Guía para principiantes:
 * - Cada vez que cambies este archivo, reinicia tu servidor
 * - Las clases que definas aquí se pueden usar en HTML como: class="mi-clase-personalizada"
 */

/** @type {import('tailwindcss').Config} */
module.exports = {
  
  // 📁 CONTENT: Le dice a Tailwind dónde buscar tus clases CSS
  // Si usas una clase como "bg-red-500" en estos archivos, Tailwind la incluirá en el CSS final
  // Si NO la usas, Tailwind la eliminará para hacer el archivo más pequeño
  content: [
    "./app/templates/**/*.html",    // 🔍 Busca en TODOS los HTML dentro de app/templates/
    "./app/static/js/**/*.js",      // 🔍 Busca en TODOS los JS dentro de app/static/js/
  ],

  // 🎨 THEME: Aquí personalizas los estilos de Tailwind
  theme: {
    
    // 🔧 EXTEND: Agrega cosas NUEVAS sin eliminar las que ya vienen con Tailwind
    // Si usas "theme" sin "extend", eliminarías todos los colores/fuentes por defecto
    extend: {
      
      // 🖋️ FUENTES PERSONALIZADAS
      // Después de definirlas aquí, las usas así: class="font-great-vibes"
      fontFamily: {
        'great-vibes': ['Great Vibes', 'cursive'],  // ✨ Para títulos elegantes
        // Ejemplo de uso: <h1 class="font-great-vibes">Valentina</h1>
      },

      // 🎨 COLORES PERSONALIZADOS TIPO COSTCO/RETAIL
      colors: { 
        'ccdr': {
          'red-primary': '#CC0000',    // Rojo principal intenso (tipo Costco)
          'red-dark': '#990000',       // Rojo oscuro para hover/activos
          'red-light': '#FF3333',      // Rojo claro para acentos
          'black': '#000000',          // Negro puro
          'gray-dark': '#1a1a1a',      // Gris muy oscuro (casi negro)
          'gray-medium': '#4a4a4a',    // Gris medio
          'gray-light': '#e5e5e5',     // Gris claro para fondos
          'white': '#ffffff',          // Blanco puro
          'cream': '#f8f8f8',          // Crema suave para fondos alternativos
        }
      },
      // Uso: class="bg-ccdr-red-primary text-ccdr-white"

      // 📏 ESPACIADO PERSONALIZADO (ejemplos)
      // spacing: {
      //   '18': '4.5rem',   // Crea class="p-18" o "m-18" para 4.5rem de padding/margin
      //   '88': '22rem',    // Crea class="h-88" para altura de 22rem
      // },

      // 📱 BREAKPOINTS PERSONALIZADOS (para responsive design)
      // screens: {
      //   'xs': '475px',      // Crea modificador xs: para pantallas pequeñas
      //   '3xl': '1600px',    // Crea modificador 3xl: para pantallas muy grandes
      // },
      // Uso: class="text-sm xs:text-base 3xl:text-xl"

      // 🖼️ TAMAÑOS PERSONALIZADOS
      // width: {
      //   '128': '32rem',     // Crea class="w-128"
      // },
      // height: {
      //   '128': '32rem',     // Crea class="h-128"
      // },

    },
  },

  // 🔌 PLUGINS: Funcionalidades extra para Tailwind
  // Los plugins agregan clases nuevas o mejoran las existentes
  plugins: [
    // Algunos plugins populares (comentados, instálalos si los necesitas):
    
    // require('@tailwindcss/forms'),          // 📝 Mejora estilos de formularios
    // require('@tailwindcss/typography'),     // 📖 Estilos para contenido de blog/artículos
    // require('@tailwindcss/aspect-ratio'),   // 📐 Control de proporciones de imágenes/videos
    // require('@tailwindcss/line-clamp'),     // ✂️ Recorta texto con "..."
  ],

  // ⚙️ CONFIGURACIONES AVANZADAS (opcional, para cuando seas más experto)
  
  // 🌙 DARK MODE: Habilita modo oscuro
  // darkMode: 'class',     // Usa class="dark" en el HTML para activar modo oscuro
  // darkMode: 'media',     // Usa las preferencias del sistema del usuario

  // 🎯 IMPORTANTE: Solo cambia estas si sabes lo que haces
  // corePlugins: {
  //   preflight: false,    // Desactiva los estilos base de Tailwind
  // },
  
  // 🏷️ PREFIJO: Agrega prefijo a todas las clases (ej: tw-bg-red-500)
  // prefix: 'tw-',
  
  // 🚫 SEPARATOR: Cambia el separador de modificadores (por defecto es :)
  // separator: '_',      // Cambiaría hover:bg-red-500 por hover_bg-red-500
}

/**
 * 💡 CONSEJOS PARA USAR ESTE ARCHIVO:
 * 
 * 1. 🔄 REINICIA el servidor después de cambiar este archivo
 * 2. 🎨 Agrega colores en 'colors' para tu marca
 * 3. 🖋️ Agrega fuentes en 'fontFamily' para tipografías especiales
 * 4. 📱 Usa 'screens' para breakpoints personalizados
 * 5. 🔍 Las rutas en 'content' deben apuntar a donde usas las clases
 * 
 * 📖 RECURSOS ÚTILES:
 * - Documentación oficial: https://tailwindcss.com/docs
 * - Colores por defecto: https://tailwindcss.com/docs/customizing-colors
 * - Fuentes por defecto: https://tailwindcss.com/docs/font-family
 * - Breakpoints por defecto: https://tailwindcss.com/docs/responsive-design
 */