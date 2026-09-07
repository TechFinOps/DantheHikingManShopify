import {Link, useLoaderData} from 'react-router';
import {Image, Money} from '@shopify/hydrogen';
import {ProductItem} from '~/components/ProductItem';

/**
 * @type {Route.MetaFunction}
 */
export const meta = () => {
  return [{title: 'DantheHikingMan | Built to sell'}];
};

/**
 * @param {Route.LoaderArgs} args
 * @returns {Promise<LoaderReturnData>}
 */
export async function loader(args) {
  const {products} = await args.context.storefront.query(HOME_PRODUCTS_QUERY, {
    cache: args.context.storefront.CacheLong(),
  });

  return {
    featuredProducts: products.nodes,
  };
}

export default function Homepage() {
  /** @type {LoaderReturnData} */
  const data = useLoaderData();
  const featuredProducts = data.featuredProducts ?? [];
  const heroProduct = featuredProducts[0];

  return (
    <div className="landing-page">
      <section className="landing-hero">
        <div className="landing-hero-copy">
          <p className="landing-eyebrow">High-converting storefront</p>
          <h1>Turn browsers into buyers with a clean, focused homepage.</h1>
          <p className="landing-intro">
            This landing page is built to do one job well: highlight the offer,
            reduce friction, and push shoppers toward the products that matter
            most.
          </p>
          <div className="landing-actions">
            <Link className="landing-button landing-button--primary" to="/collections/all">
              Shop products
            </Link>
            <Link className="landing-button landing-button--secondary" to="#featured-products">
              See featured picks
            </Link>
          </div>
          <ul className="landing-points" aria-label="Store highlights">
            <li>Clear headline and call to action</li>
            <li>Mobile-first, easy-to-scan layout</li>
            <li>Built to showcase real products fast</li>
          </ul>
        </div>

        <div className="landing-hero-panel">
          {heroProduct ? (
            <Link className="landing-product-spotlight" to={`/products/${heroProduct.handle}`}>
              <p className="landing-eyebrow">Featured product</p>
              {heroProduct.featuredImage ? (
                <div className="landing-product-spotlight-media">
                  <Image
                    alt={heroProduct.featuredImage.altText || heroProduct.title}
                    aspectRatio="1/1"
                    data={heroProduct.featuredImage}
                    loading="eager"
                    sizes="(min-width: 45em) 420px, 100vw"
                  />
                </div>
              ) : null}
              <div className="landing-product-spotlight-copy">
                <h2>{heroProduct.title}</h2>
                <p className="landing-product-spotlight-price">
                  <Money data={heroProduct.priceRange.minVariantPrice} />
                </p>
                <span className="landing-button landing-button--primary">
                  Shop this item
                </span>
              </div>
            </Link>
          ) : (
            <div className="landing-stat-card">
              <p>Best for</p>
              <h2>One strong offer at a time</h2>
              <p>
                Perfect for a hero product, starter bundle, seasonal drop, or any
                collection you want buyers to notice first.
              </p>
            </div>
          )}
          <div className="landing-stat-grid" aria-label="Sales benefits">
            <div>
              <strong>1</strong>
              <span>primary message</span>
            </div>
            <div>
              <strong>3</strong>
              <span>benefits at a glance</span>
            </div>
            <div>
              <strong>4</strong>
              <span>featured products max</span>
            </div>
          </div>
        </div>
      </section>

      <section className="landing-value-strip" aria-label="Why this works">
        <article>
          <h3>Sell the outcome</h3>
          <p>Lead with the result people want, not a wall of menu links.</p>
        </article>
        <article>
          <h3>Lower hesitation</h3>
          <p>Use short sections, concise copy, and fewer clicks to reach checkout.</p>
        </article>
        <article>
          <h3>Show the proof</h3>
          <p>Make room for featured products, reviews, or a single strong bundle.</p>
        </article>
      </section>

      <section className="landing-products" id="featured-products">
        <div className="landing-section-heading">
          <p className="landing-eyebrow">Featured products</p>
          <h2>Start with the products you want to move first.</h2>
        </div>

        {featuredProducts.length ? (
          <div className="products-grid landing-products-grid">
            {featuredProducts.map((product) => (
              <ProductItem key={product.id} product={product} loading="lazy" />
            ))}
          </div>
        ) : (
          <div className="landing-empty-state">
            <h3>No products yet</h3>
            <p>
              Add products in Shopify, then come back here and the homepage will
              showcase them automatically.
            </p>
            <Link className="landing-button landing-button--primary" to="/collections/all">
              Browse the store
            </Link>
          </div>
        )}
      </section>

      <section className="landing-closeout">
        <div>
          <p className="landing-eyebrow">Next step</p>
          <h2>Swap in your real offer and let the page do the selling.</h2>
        </div>
        <Link className="landing-button landing-button--primary" to="/collections/all">
          Shop now
        </Link>
      </section>
    </div>
  );
}

const HOME_PRODUCTS_QUERY = `#graphql
  fragment HomeProduct on Product {
    id
    title
    handle
    priceRange {
      minVariantPrice {
        amount
        currencyCode
      }
    }
    featuredImage {
      id
      url
      altText
      width
      height
    }
  }
  query HomeProducts {
    products(first: 4, sortKey: UPDATED_AT, reverse: true) {
      nodes {
        ...HomeProduct
      }
    }
  }
`;

/** @typedef {import('./+types/_index').Route} Route */
/** @typedef {import('storefrontapi.generated').HomeProductFragment} HomeProductFragment */
/** @typedef {import('@shopify/remix-oxygen').SerializeFrom<typeof loader>} LoaderReturnData */
