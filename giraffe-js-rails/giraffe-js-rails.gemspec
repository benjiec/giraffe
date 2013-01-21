# -*- encoding: utf-8 -*-
require File.expand_path('lib/giraffe-js-rails/version', __FILE__)

Gem::Specification.new do |gem|
  gem.authors       = ["Benjie Chen"]
  gem.email         = ["benjie@alum.mit.edu"]
  gem.description   = %q{Use Giraffe Javascript files with Rails}
  gem.summary       = %q{Use Giraffe Javascript files with Rails}
  gem.homepage      = ""

  gem.add_dependency "railties", "> 3.1"
  gem.add_dependency "raphael-rails"

  gem.files         = `git ls-files`.split($\)
  gem.name          = "giraffe-js-rails"
  gem.require_paths = ["lib"]
  gem.version       = GiraffeJs::Rails::VERSION
end

