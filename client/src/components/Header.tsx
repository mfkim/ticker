import {Link} from "react-router-dom";

export default function Header() {
  return (
    <header
      className="sticky top-0 z-50 w-full border-b border-rh-gray bg-rh-black/95 backdrop-blur-md supports-[backdrop-filter]:bg-rh-black/60">
      <div className="flex h-16 items-center justify-between px-6 max-w-[1600px] mx-auto">

        {/* Logo */}
        <Link to="/" className="flex items-center gap-2 cursor-pointer group">
          <svg
            className="w-8 h-8 text-rh-green transition-transform group-hover:scale-110"
            viewBox="0 0 24 24"
            fill="currentColor"
          >
            <path
              d="M12 2L2 7l10 5 10-5-10-5zm0 9l2.5-1.25L12 8.5l-2.5 1.25L12 11zm0 2.5l-5-2.5-5 2.5L12 22l10-8.5-5-2.5-5 2.5z"/>
          </svg>
          <span className="text-xl font-black tracking-tighter text-rh-text">
              TICKER
            </span>
        </Link>

        {/* Search Bar (Desktop Only) */}
        <div className="hidden md:flex flex-1 max-w-md mx-8">
          <div className="relative w-full group">
            <div className="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
              <svg className="w-5 h-5 text-rh-subtext group-focus-within:text-rh-green transition-colors" fill="none"
                   stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2"
                      d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
              </svg>
            </div>
            <input
              type="text"
              className="block w-full py-2.5 pl-10 pr-4 text-sm font-medium text-rh-text bg-rh-dark border border-transparent rounded-full
                             placeholder-rh-subtext focus:bg-rh-black focus:border-rh-green focus:ring-1 focus:ring-rh-green focus:outline-none transition-all"
              placeholder="Search"
            />
          </div>
        </div>

        {/* Navigation */}
        <nav className="hidden md:flex items-center gap-8 text-sm font-bold text-rh-text">
          {['Dow 30', 'S&P 500', 'NASDAQ', 'VIX'].map((item) => (
            <a
              key={item}
              href="#"
              className="hover:text-rh-green transition-colors"
            >
              {item}
            </a>
          ))}
        </nav>

        {/* Menu (Mobile) */}
        <button className="md:hidden text-rh-text hover:text-rh-green">
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6h16M4 12h16M4 18h16"></path>
          </svg>
        </button>

      </div>
    </header>
  );
}
